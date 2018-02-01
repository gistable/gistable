import atexit
import subprocess
from django.core.management.commands.runserver import BaseRunserverCommand
from django.core.servers.basehttp import AdminMediaHandler
from django.conf import settings

# Patch runserver to run the sass and coffeesscript compilers automatically
class Command(BaseRunserverCommand):
    active_processes = []

    def _run_shell_cmd(self, cmd):
        print "Running command: %s" % cmd
        proc = subprocess.Popen(
            [cmd],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr
        )
        self.active_processes.append(proc)

    def get_handler(self, *args, **options):
        """
        Serves admin media like old-school (deprecation pending).
        """
        handler = super(Command, self).get_handler(*args, **options)
        return AdminMediaHandler(handler, options.get('admin_media_path'))

    def inner_run(self, *args, **options):
        static_dir = settings.STATIC_ROOT.replace(settings.PROJECT_PATH + "/", "") + "/"
        self._run_shell_cmd("sass --watch %ssass:%scss" % (static_dir, static_dir))
        self._run_shell_cmd("coffee --watch --output %sjs/ --compile %scoffee/" % (static_dir, static_dir))
        super(Command, self).inner_run(*args, **options)

    # NOTE: This process kills sass and coffee script when either the runserver command
    # is closed in the terminal or it's reloaded by a code change
    def exit(self):
        for proc in self.active_processes:
            proc.terminate()

    def __init__(self, *args, **kwargs):
        atexit.register(self.exit)
        return super(Command, self).__init__(*args, **kwargs)
