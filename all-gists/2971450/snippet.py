"""Convert datetimes in the database when switching USE_TZ from False to True.

tl;dr RUNNING THIS SCRIPT CAN RESULT IN DATA CORRUPTION, DATA LOSS AND EVEN
      SERVER CRASHES. USE IT AT YOUR OWN RISK. NO WARRANTY WHATSOEVER.

This is a management command. Put it in the management.commands package of
one of your applications, then run: ./manage.py convert_to_utc <app_name> ...

This script assumes that no write operations take place while it's running.
It will rewrite every single record in your database; that's its whole point.
It will crash and burn if a datetime is non-existent or ambiguous in local
time, that is, if it falls during the DST switch -- crystal balls don't exist.
It wraps the conversion for each model in a transaction in order to maintain
consistency at the table level. However, if something goes wrong, you'll still
end up with a half-converted database, where some tables are converted and
others aren't. If this happens, I'm sorry, but you're on your own to fix it.

Please, benchmark dry runs on a copy of your database and make a backup before
attempting to run this on a production server. Shut down your website while
the script runs. If your website is sufficiently large that you can't afford
the downtime, then this script isn't sufficiently sophisticated for you.
"""

import warnings
warnings.filterwarnings(
        'ignore', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')

from django.core.management.base import AppCommand
from django.db import connections, models, transaction
from django.test.utils import override_settings


class Command(AppCommand):
    help = "Converts to UTC datetimes stored for models of the given app name(s)."

    def handle(self, *args, **options):
        if len(connections.all()) > 1:
            raise CommandError(u"This script isn't tested with multiple databases. "
                               u"Edit the source if you want to run it anyway.")
        for connection in connections.all():
            if connection.ops.set_time_zone_sql():
                raise CommandError(u"Your database backend appears to support time zones. "
                                   u"You problably shouldn't run this script.")
        return super(Command, self).handle(*args, **options)

    def handle_app(self, app, **options):
        for model in models.get_models(app):
            meta = model._meta
            self.stdout.write(u"%s.%s: " % (meta.app_label, meta.object_name))
            if meta.proxy:
                self.stdout.write(u"OK (proxy model)\n")
                continue
            fields = [f.name for f in meta.local_fields if isinstance(f, models.DateTimeField)]
            if not fields:
                self.stdout.write(u"OK (no datetime fields)\n")
                continue
            self.stdout.write(u"fields to convert: %s\n" % u" ".join(fields))
            with transaction.commit_on_success():
                with override_settings(USE_TZ=False):
                    for obj in model.objects.all().only(*fields).iterator():
                        with override_settings(USE_TZ=True):
                            # Bypass model.save() to preserve auto_now fields
                            values = dict((f, getattr(obj, f)) for f in fields)
                            model.objects.filter(pk=obj.pk).update(**values)
