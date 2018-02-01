import os
import subprocess
import atexit
import signal
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunserverCommand

class Command(RunserverCommand):
    option_list = RunserverCommand.option_list + (
        make_option('--compasswatch', dest='compass_project_path', default=settings.COMPASS_PROJECT_PATH,
            help='Specifies the project directory for a compass project'),
    )

    def run(self, *args, **options):
        """Runs the server and the compass watch process"""
        use_reloader = options.get('use_reloader')
        
        if settings.DEBUG and use_reloader and os.environ.get("RUN_MAIN") != "true":
            """RUN_MAIN Environment variable is set to None the first time the
            runserver command is start, on every reload after a code change if the
            option 'use_reloader' is set (by default it's) RUN_MAIN is set on 'true'.
            """

            self.compass_project_path = options.get('compass_project_path')

            if not os.path.exists(os.path.join(self.compass_project_path, 'config.rb')):
                self.stdout.write('>>> Didn\'t found a Compass project in %r\n' % self.compass_project_path)
            else:
                self.start_compass_watch()

        super(Command, self).run(*args, **options)


    def start_compass_watch(self):
        self.stdout.write(self.style.NOTICE(">>> Starting the compass watch command for %r") % self.compass_project_path + "\n" )
        self.compass_process = subprocess.Popen(
            ['compass watch %s' % self.compass_project_path],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr,
        )
        self.stdout.write(self.style.NOTICE(">>> Compass watch process on pid %r" % self.compass_process.pid) + "\n")

        def kill_compass_project(pid):
            self.stdout.write(self.style.NOTICE(">>> Closing Compass watch process") + "\n")
            os.kill(pid, signal.SIGTERM)

        atexit.register(kill_compass_project, self.compass_process.pid)