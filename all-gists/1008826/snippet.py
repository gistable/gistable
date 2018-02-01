# Class for managing multiple servers or anything with start() and stop() methods

class ServerRack(object):

    def __init__(self, servers):
        self.servers = servers

    def start(self):
        started = []
        try:
            for server in self.servers[:]:
                server.start()
                started.append(server)
                name = getattr(server, 'name', None) or server.__class__.__name__ or 'Server'
                log('%s started on %s', name, server.address)
        except:
            self.stop(started)
            raise

    def stop(self, servers=None):
        if servers is None:
            servers = self.servers[:]
        for server in servers:
            try:
                server.stop()
            except:
                if hasattr(server, 'loop'): # gevent >= 1.0
                    server.loop.handle_error(server.stop, *sys.exc_info())
                else: # gevent <= 0.13
                    import traceback
                    traceback.print_exc()


# example: run WSGI app on HTTP and HTTPS
rack = ServerRack([WSGIServer(('', 80), application)),
                   WSGIServer(('', 443), application, keyfile=keyfile, certfile=certfile])
rack.start()