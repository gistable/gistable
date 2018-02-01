#!/usr/bin/env python

import cherrypy
from cherrypy import _cprequest
from cherrypy.lib import httputil
import sys
import logging
from cherrypy.process import servers

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


LOGGER = logging.getLogger(__name__)


def patch_cherrypy():
    cherrypy.serving = GreenletServing()


class GreenletServing(object):
    __slots__ = ('__local__', )

    def __init__(self):
        object.__setattr__(self, '__local__', {
        })
        ident = get_ident()
        self.__local__[ident] = {
            'request': _cprequest.Request(httputil.Host("127.0.0.1", 80), httputil.Host("127.0.0.1", 1111)),
            'response': _cprequest.Response()
        }

    def load(self, request, response):
        self.__local__[get_ident()] = {
            'request': request,
            'response': response
        }

    def __getattr__(self, name):
        try:
            return self.__local__[get_ident()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = get_ident()
        local = self.__local__
        try:
            local[ident][name] = value
        except KeyError:
            local[ident] = {name: value}

    def clear(self):
        """Clear all attributes of the current greenlet."""
        del self.__local__[get_ident()]


class GeventWSGIServer(object):

    """Adapter for a gevent.wsgi.WSGIServer."""

    def __init__(self, *args, **kwargs):
        patch_cherrypy()
        self.args = args
        self.kwargs = kwargs
        self.ready = False

    def start(self):
        """Start the GeventWSGIServer."""
        # We have to instantiate the server class here because its __init__
        # starts a threadpool. If we do it too early, daemonize won't work.
        from gevent.wsgi import WSGIServer

        self.ready = True
        LOGGER.debug('Starting Gevent WSGI Server...')
        self.httpd = WSGIServer(*self.args, **self.kwargs)
        self.httpd.serve_forever()

    def stop(self):
        """Stop the HTTP server."""
        LOGGER.debug('Stoping Gevent WSGI Server...')
        self.ready = False
        self.httpd.stop()


class WebServer(object):

    def __init__(self, server_name='Sola', host='127.0.0.1', port=8080, use_gevent=True, debug=False, encoding='utf-8'):
        self.server_name = server_name
        self.ready = False
        self.host = host
        self.port = port
        self.debug = debug
        self.encoding = encoding
        self.use_gevent = use_gevent
        self.config = self.gen_config()
        self.bootstrap()

    def asset(self, path, asset_path):
        """Mount Static directory"""
        self.config[path] = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': asset_path
        }

    def gen_config(self):
        conf = {
            'global':
                {
                    'server.socket_host': self.host,
                    'server.socket_port': self.port,
                    'engine.autoreload.on': self.debug,
                    #'log.screen': self.debug,
                    'log.error_file': '',
                    'log.access_file': '',


                    'tools.decode.on': unicode,
                    'tools.encode.on': unicode,
                    'tools.encode.encoding': self.encoding,
                    'tools.gzip.on': True,
                    'tools.log_headers.on': False,
                    'request.show_tracebacks': False,
                }
        }
        if self.use_gevent:
            conf['global']['environment'] = 'embedded'

        return conf

    def bootstrap(self):
        self.bootstrap_options()
        self.boostrap_command_parse()
        self.boostrap_database_configuration()

    def bootstrap_options(self):
        pass

    def boostrap_database_configuration(self):
        pass

    def boostrap_command_parse(self):
        pass

    def new_route(self):
        return cherrypy.dispatch.RoutesDispatcher()

    def create_app(self):
        raise NotImplemented('Must implement create_app in Subclass')

    def _bootstrap_app(self):
        ctl, routes = self.create_app()
        cherrypy.config.clear()
        config = {'/': {'request.dispatch': routes}, 'global': self.config}
        config.update(self.config)
        cherrypy.config.update(config)
        return cherrypy.tree.mount(ctl, '/', config)

    def serve_forever(self):
        engine = cherrypy.engine
        if hasattr(engine, "signal_handler"):
            engine.signal_handler.subscribe()
        if hasattr(engine, "console_control_handler"):
            engine.console_control_handler.subscribe()
        app = self._bootstrap_app()
        try:
            if self.use_gevent:
                # Turn off autoreload when using *cgi.
                #cherrypy.config.update({'engine.autoreload_on': False})
                addr = cherrypy.server.bind_addr
                cherrypy.server.unsubscribe()
                f = GeventWSGIServer(addr, app, log=None)
                s = servers.ServerAdapter(engine, httpserver=f, bind_addr=addr)
                s.subscribe()
                engine.start()
            else:
                cherrypy.quickstart(app)
        except KeyboardInterrupt:
            self.stop()
        else:
            engine.block()

    def stop(self):
        cherrypy.engine.stop()


class HelloController(object):

    def index(self):
        return 'Index Page'

    def get(self, name='Test'):
        return "Name: " + name

    def page(self, page=1):
        return 'Page %s' % (page)


class Helloserver(WebServer):

    def create_app(self):
        ctl = HelloController()
        m = self.new_route()
        m.mapper.explicit = False
        m.connect('index', '/', controller=ctl, action='index')
        m.connect('get', '/get', controller=ctl, action='get')
        m.connect('page', '/page', controller=ctl, action='page')
        m.connect('page', '/page/:page', controller=ctl, action='page')
        return ctl, m


def run(host='localhost', port=80, use_gevent=True, debug=False):
    setdebug(debug)
    Helloserver(server_name='HelloServer', host=host,
                port=port, use_gevent=use_gevent, debug=debug).serve_forever()


def setdebug(debug=False):

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

if __name__ == '__main__':
    run(debug=True)
