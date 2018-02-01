from django.core.management.base import BaseCommand
from mymodule import main
import logging


class Command(BaseCommand):
    help = 'Do foo'

    def handle(self, *args, **options):

        # Setup logging
        #
        # Verbosity levels:
        #   1 - prints nothing
        #   2 - Prints log messages for just this module
        #   3 or greater - Prints log messages from any module
        options['verbosity'] = int(options['verbosity'])
        if options['verbosity'] > 1:
            if options['verbosity'] == 2:
                # use logger for just this module
                logger = logging.getLogger('mymodule')
            else:
                # use root logger
                logger = logging.getLogger('')
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(console)

        main()
