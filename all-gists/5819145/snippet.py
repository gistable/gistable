import commands
import os

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from trapeze import settings as trapeze_settings


class Command(BaseCommand):
    help = 'Dumps database and files to devdata'
    option_list = BaseCommand.option_list + (
        make_option('--path', action='store', dest='path', type='string',
            help='Path to devdata folder'),
    )

    def handle(self, **options):
        path = options.get('path') or trapeze_settings.PATH_TO_DEVDATA
        if not os.path.exists(path):
            self.stderr.write('Devdata path does not exist: %s\n' % path)
            return

        devdata_files = os.path.join(path, 'files')
        media_files = settings.MEDIA_ROOT

        if not os.path.exists(media_files):
            self.stderr.write('Media files path does not exist: %s\n' % media_files)

        # Perform sql dump
        dump_sql = os.path.join(path, 'dump.sql')
        pg_dump = 'pg_dump -h %(host)s -U %(user)s --clean --no-owner --no-privileges %(db)s > %(dump_sql)s' % {
            'host': settings.DATABASES['default']['HOST'], 'user': settings.DATABASES['default']['USER'],
            'db': settings.DATABASES['default']['NAME'], 'dump_sql': dump_sql,
        }
        status, output = commands.getstatusoutput(pg_dump)
        if status != 0:
            self.stderr.write(output + "\n")
            return
        else:
            self.stdout.write(output + "\n")

        # Rsync media files
        if not os.path.exists(devdata_files):
            os.mkdir(devdata_files)

        rsync_files = 'rsync %(options)s %(media_files)s %(devdata_files)s ' % {
            'devdata_files': devdata_files,
            'media_files': media_files,
            'options': trapeze_settings.RSYNC_OPTIONS,
        }
        status, output = commands.getstatusoutput(rsync_files)
        self.stdout.write(output)
        if status != 0:
            self.stderr.write(output + "\n")
        else:
            self.stdout.write(output + "\n")
