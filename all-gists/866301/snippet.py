import os, sys


class Winpdb(object):
    '''Embed a Winpdb server.

    If you have to tunnel to connect remotely from the Winpdb client, run:

        ssh -C -N -f -L 51000:localhost:51000 $SERVER_HOST

    Requires rpdb2 (http://pypi.python.org/pypi/winpdb)
    '''
    def __init__(self, password='password'):
        self.password = password
        self.started = False

    def set_trace(self):
        from rpdb2 import start_embedded_debugger
        if not self.started:
            print >> sys.stderr, 'Starting Winpdb server (pid=%d)' % os.getpid()
            start_embedded_debugger(self.password, fAllowRemote=True)
            self.started = True


class Komodopdb(object):
    """Komodo IDE remote debugger client.

    Requires dbgp (http://pypi.python.org/pypi/dbgp)
    """
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.started = False

    def set_trace(self):
        from dbgp.client import brk
        if not self.started:
            print >> sys.stderr, 'Starting dbgp client (pid=%d)' % os.getpid()
            brk(host=self.host, port=self.port)
            self.started = True


if __name__ == "__main__":
    import dumbo
    set_trace = Winpdb().set_trace
    #set_trace = Komodopdb().set_trace

    def mapper(key, value):
        set_trace()
        yield value.split(" ")[0], 1

    def reducer(key, values):
        set_trace()
        yield key, sum(values)

    dumbo.run(mapper, reducer)
