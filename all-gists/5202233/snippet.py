from __future__ import print_function

import sys
sys.path.append('/opt/pycharm/pycharm-2.7.1/pycharm-debug-py3k.egg')

#import pydevd
#pydevd.settrace('localhost', port=9989, stdoutToServer=True, stderrToServer=True)

import ipdb
#ipdb.set_trace()
#from ipdb import launch_ipdb_on_exception

import tornado.ioloop
import tornado.web

class DebuggingLoop(tornado.ioloop.IOLoop):
    def handle_callback_exception(self, callback):
        exc_type, exc_value, tb = sys.exc_info()
        ipdb.post_mortem(tb)

ioloop = DebuggingLoop()
ioloop.install()

class DebuggingRequest(tornado.web.RequestHandler):

    def _handle_request_exception(self, e):
        tornado.web.RequestHandler._handle_request_exception(self, e)
        exc_type, exc_value, tb = sys.exc_info()
        ipdb.post_mortem(tb)

def init_ipython():
    from IPython.config.loader import Config
    from IPython.frontend.terminal.embed import InteractiveShellEmbed

    try:
        get_ipython
    except NameError:
        nested = 0
        cfg = Config()
    else:
        print("Running nested copies of IPython.")
        print("The prompts for the nested copy have been modified")
        cfg = Config()
        nested = 1

    ipshell = InteractiveShellEmbed(config=cfg,
            banner1 = 'Stopping IO Loop and dropping to ipython')

    class shell_wrapper(object):

        def __init__(self):
            self.user_wants_out = False

        def __call__(self):
            ipshell('Ctrl-D, quit, exit all exit interpreter and continue program\n'
                    'If you need to kill the program %kill', stack_depth=3)
            return self.user_wants_out

    _shell_wrapper = shell_wrapper()

    def kill_program(self, parameter_s=''):
        _shell_wrapper.user_wants_out = True
        ipshell.exit()

    def really_die(self, etype, value, tb, tb_offset=None):
        _shell_wrapper.user_wants_out = True
        return None

    ipshell.define_magic("kill", kill_program)
    ipshell.confirm_exit = False
    ipshell.set_custom_exc((SystemExit,), really_die)

    return _shell_wrapper

IPSHELL = init_ipython()

def drop_to_shell(ipshell=IPSHELL):
    if ipshell:
        exit = ipshell()
        if exit:
            sys.exit(0)

def run_loop(ioloop):
    while True:
        try:
            ioloop.start()
        except KeyboardInterrupt:
            ioloop.stop()
            drop_to_shell()
            print('Resuming I/O loop')


## ALL OF THE ABOVE WILL DISAPPEAR INTO A MODULE

class MainHandler(DebuggingRequest):
    def get(self):
        something = ['this', 'is', 'the', 'response']
        drop_to_shell()
        self.write(' '.join(something))

class Broken(DebuggingRequest):
    def get(self):
        raise NotImplemented()

app = tornado.web.Application([
    (r'/', MainHandler),
    (r'/test', Broken)
], debug=True)

if __name__ == '__main__':
    app.listen(8000)
    ioloop.add_callback(lambda: sys.stdout.write('Started on port 8000 <CTRL>-C to abort\n'))
    run_loop(ioloop)