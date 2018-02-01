# vim: tabstop=4 shiftwidth=4 softtabstop=4
#!/usr/bin/python
import sys
import time
import logging
from daemon import runner
#
# An example daemon main logic application class.
# Just keep writing timestamps to a log file periodically.
#
class App:
    def __init__(self):
        # python-daemon DaemonRunner requires the below.
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        # For debug, you can use '/dev/tty' for stdout/stderr instead.
        #self.stdout_path = '/dev/tty'
        #self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/foo.pid'
        self.pidfile_timeout = 5
        # The above 5 attributes are mandatory.
        #
        # The below are this App specific. (conf file is not implemented now)
        self.log_file = '/tmp/foobar.log'
        self.conf_file = '/etc/pdaemon.conf'
        self.foreground = False

    def run(self):
        # Here is your main logic.
        # Initializing code.
        if not self.foreground:
            logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename=self.log_file,
                            filemode='a')
        while True:
            # the main loop code.
            try:
                str = time.asctime(time.localtime(time.time()))
                if self.foreground:
                    print str
                else:
                    logging.info('DEBUG: %s' % str)

                time.sleep(1)
            except:
                logging.info(sys.exc_info())
                logging.info('Terminating.')
                sys.exit(1)
#
# An example extension of runner.DaemonRunner class of python-daemon.
# Improvement points are:
#   - Natual unix getopt style option.
class MyDaemonRunner(runner.DaemonRunner):
    def __init__(self, app):
        # workaround... :(
        self.app_save = app

        self.detach_process = True
        runner.DaemonRunner.__init__(self, app)

    def parse_args(self, argv=None):
        # Note that DaemonRunner implements its own parse_args(), and
        # it is called in __init__ of the class.
        # Here, we override it following unix getopt style syntax.
        import getopt

        try:
            opts, args = getopt.getopt(sys.argv[1:],
                                        'skrl:p:fvh',
                                       ['start', 'kill', 'log_file=',
                                        'pid_file=', 'foreground'])
        except getopt.GetoptError:
            print sys.exc_info()
            print 'getopt error...'
            sys.exit(2)

        self.action = ''
        for opt, arg in opts:
            #print 'opt / arg :', opt, arg
            if opt in ('-s'):
                self.action = 'start'

            elif opt in ('-k'):
                self.action = 'stop'

            elif opt in ('-r'):
                self.action = 'restart'

            elif opt in ('-l', '--log_file'):
                # log_file is stored in the App object. But, here it's
                # pointed by 'app_save' attribute of MyDaemonRunner,
                # not by 'app'. This is because __init__ of DaemonRunner
                # calls parse_args() BEFORE recording app reference... :(
                self.app_save.log_file = arg
                # print 'setting log_file :' , self.app_save.log_file

            elif opt in ('-p', '--pidfile'):
                self.app_save.pidfile_path = arg
                #print 'arg is :', arg

            elif opt in ('-f', '--foreground'):
                self.detach_process = False
                self.app_save.stdout_path = '/dev/tty'
                self.app_save.stderr_path = '/dev/tty'
                self.app_save.foreground = True

            elif opt in ('-v'):
                self.verbose = True

            elif opt in ('-h', '--help'):
                print 'show usage...'
                sys.exit(2)

            else:
                print 'show usage'
                sys.exit(2)

        if not self.action:
            print sys.argv[0] + ' (-s|-k|-r) [options]'
            sys.exit(1)
    #
    # FYI: The original parse_args() in runner.DaemonRunner class.
    #
    def original_parse_args(self, argv=None):
        """ Parse command-line arguments.
            """
        if argv is None:
            argv = sys.argv

        min_args = 2
        if len(argv) < min_args:
            self._usage_exit(argv)

        self.action = argv[1]
        if self.action not in self.action_funcs:
            self._usage_exit(argv)
#
#
#
if __name__ == '__main__':
    app = App()
    daemon_runner = MyDaemonRunner(app)
    if not app.foreground:
        daemon_runner.do_action()
    else:
        app.run()
