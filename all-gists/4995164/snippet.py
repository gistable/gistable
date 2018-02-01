from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db.models.signals import post_syncdb
from south.models import MigrationHistory
import pizzanuvola_teaser.settings as settings


def migration_exists(appname, migrationnumber):
    appname = appname.split('.')[-1]
    return MigrationHistory.objects.filter(app_name=appname, migration__icontains=migrationnumber).exists()


def load_data(app, sender, **kwargs):
    if app.__name__ == settings.INSTALLED_APPS[-1] + ".models":
        migrations = {
            'allauth.socialaccount': [
                '0001',
                '0002',
                '0003',
                '0004',
                '0005',
                '0006',
                '0007',
                '0008',
            ],
            'allauth.socialaccount.providers.facebook': [
                '0001',
                '0002',
            ],
        }

        for appname, migrationlist in migrations.iteritems():
            for migration in migrationlist:
                if not migration_exists(appname, migration):
                    try:
                        call_command('migrate', appname, migration)
                    except ImproperlyConfigured:
                        pass

post_syncdb.connect(load_data)
