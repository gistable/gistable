import os
import socket
import urllib
import urlparse
import cherrypy
 
 
# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
# Celery loader
os.environ['CELERY_LOADER'] = 'djcelery.loaders.DjangoLoader'
 
 
class DjangoApplication(object):
    def __init__(self):
        self.servers = []
        self.domains = {}
 
    def add_server(self, netloc, path, config):
        """Add a new CherryPy Application for a Virtual Host.
 
        Creates a new CherryPy WSGI Server instance if the host resolves
        to a different IP address or port.
 
        """
        from cherrypy._cpwsgi_server import CPWSGIServer
        from cherrypy.process.servers import ServerAdapter
 
        host, port = urllib.splitnport(netloc, 80)
        host = socket.gethostbyname(host)
        bind_addr = (host, port)
        if bind_addr not in self.servers:
            self.servers.append(bind_addr)
            server = CPWSGIServer()
            server.bind_addr = bind_addr
            adapter = ServerAdapter(cherrypy.engine, server, server.bind_addr)
            adapter.subscribe()
        self.domains[netloc] = cherrypy.Application(root=None,
            config={path.rstrip('/') or '/': config})
 
    def cfg_assets(self, url, root):
        """Configure hosting of static and media asset directories.
 
        Can either mount to a specific path or add a Virtual Host. Sets
        Expires header to 1 year.
 
        """
        url_parts = urlparse.urlsplit(url)
        path = url_parts.path.rstrip('/')
        config = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': root,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 24 * 365, # 1 year
            'tools.gzip.on': True,
            'tools.gzip.mime_types': [
                'text/*',
                'application/javascript',
                'application/x-javascript',
            ],
        }
        if url_parts.netloc:
            self.add_server(url_parts.netloc, path, config)
        elif path:
            cherrypy.tree.mount(None, path, {'/': config})
 
    def cfg_favicon(self, root):
        """Configure a default favicon.
 
        Expects it to be in STATIC_ROOT.
 
        """
        favicon = os.path.join(root, 'favicon.ico')
        config = {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': favicon,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 24 * 365, # 1 year
        }
        cherrypy.tree.mount(None, '/favicon.ico', {'/': config})
 
    def run(self, netloc='localhost:8000', reload=True, log=True):
        """Run the CherryPy server."""
        from django.conf import settings
        from django.core.handlers.wsgi import WSGIHandler
        from translogger import TransLogger
 
        host, port = urllib.splitnport(netloc, 80)
        host = socket.gethostbyname(host)
        cherrypy.config.update({
            'server.socket_host': host,
            'server.socket_port': port,
            'log.screen': log,
            'engine.autoreload_on': reload,
        })
        self.cfg_assets(settings.MEDIA_URL, settings.MEDIA_ROOT)
        self.cfg_assets(settings.STATIC_URL, settings.STATIC_ROOT)
        self.cfg_favicon(settings.STATIC_ROOT)
        app = WSGIHandler()
        app = TransLogger(app, logger_name='cherrypy.access',
                          setup_console_handler=False)
        if self.domains:
            app = cherrypy.wsgi.VirtualHost(app, self.domains)
        cherrypy.tree.graft(app)
        cherrypy.engine.start()
        cherrypy.engine.block()
 
 
def main(**kwargs):
    app = DjangoApplication()
    app.run(**kwargs)
 
 
if __name__ == '__main__':
    import argparse
 
    parser = argparse.ArgumentParser(prog='cherrypy_server',
        description='Starts a CherryPy web server for a Django application.')
    parser.add_argument('netloc', default='localhost:8000',
        metavar='optional host name, or ipaddr:port', nargs='?')
    parser.add_argument('--noreload', dest='reload', action='store_false',
        default=True, help='Tells CherryPy to NOT use the auto-reloader.')
    parser.add_argument('--nolog', dest='log', action='store_false',
        default=True, help='Tells CherryPy to NOT log web requests.')
    args = parser.parse_args()
 
    main(netloc=args.netloc, reload=args.reload, log=args.log)
