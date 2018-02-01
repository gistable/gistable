#!/usr/bin/env python
import logging

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpclient


class Manager(object):
    def __init__(self, *args, **kwargs):
        self.client = tornado.httpclient.AsyncHTTPClient()
        self.map = {}
        self.hits = {}
        self.responses = {}

    def fetch(self, url):
        def on_fetch(response):
            self.response(url, response.body)

        self.hits[url] = self.hits.get(url, 0) + 1

        self.client.fetch(url, callback=on_fetch)

    def response(self, url, value):
        while self.map[url]:
            self.responses[url] = self.responses.get(url, 0) + 1
            self.map[url].pop()(value)

    def get(self, url, callback=None):
        if self.map.get(url):
            self.map[url].append(callback)
        else:
            self.map[url] = [callback]

            self.fetch(url)


class MainHandler(tornado.web.RequestHandler):
    @property
    def manager(self):
        return self.settings['manager']

    @property
    def endpoint(self):
        return self.settings['endpoint']

    def callback(self, value):
        self.write(value)

        self.finish()

        logging.info(self.manager.hits)
        logging.info(self.manager.responses)

    @tornado.web.asynchronous
    def get(self):
        self.set_header('Content-Type', 'application/json')

        q = self.get_argument('q', 'Kiev')

        self.manager.get(self.endpoint % q, callback=self.callback)


application = tornado.web.Application(
    [
        (r'/', MainHandler),
    ],
    debug=True,
    manager=Manager(),
    endpoint='http://api.openweathermap.org/data/2.5/weather?q=%s'
)


if __name__ == '__main__':
    tornado.options.parse_command_line()

    application.listen(7777)

    tornado.ioloop.IOLoop.instance().start()
