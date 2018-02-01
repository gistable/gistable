#!/usr/bin/env python
'''
Mocking Httpclient and AsyncHttpclient in Tornado Server
'''

import unittest
import urllib
import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.httpclient
from StringIO import StringIO
from mock import patch, MagicMock
from tornado.concurrent import Future
from tornado.testing import AsyncHTTPTestCase,AsyncTestCase,AsyncHTTPClient
from tornado.httpclient import HTTPResponse, HTTPRequest, HTTPError

class TestHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        ' Makes a AsyncHttp call'

        def cb(result):
            self.write(result.body)
            self.finish()

        http_client = tornado.httpclient.AsyncHTTPClient()
        req = tornado.httpclient.HTTPRequest("http://google.com")
        http_client.fetch(req,cb)
    
    def post(self,*args,**kwargs):
        ' Makes a sync http call'
        
        http_client = tornado.httpclient.HTTPClient()
        req = tornado.httpclient.HTTPRequest("http://google.com")
        resp = http_client.fetch(req)
        self.write(resp.body)
        self.finish()

class TestServices(AsyncHTTPTestCase):
    def setUp(self):
        super(TestServices, self).setUp()
        #create un-mocked httpclients for use of testcases later
        self.real_httpclient = tornado.httpclient.HTTPClient()
        self.real_asynchttpclient = tornado.httpclient.AsyncHTTPClient(self.io_loop)
        self.sync_patcher = patch('tornado.httpclient.HTTPClient')
        self.async_patcher = patch('tornado.httpclient.AsyncHTTPClient')
        self.mock_client = self.sync_patcher.start()
        self.mock_async_client = self.async_patcher.start()

    def get_app(self):
        return application
    
    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def tearDown(self):
        self.sync_patcher.stop()
        self.async_patcher.stop()

    def test_synchttpclient(self):
        request = HTTPRequest('http://google.com')
        response = HTTPResponse(request, 200,
                                buffer=StringIO('some text'))
        self.mock_client().fetch.side_effect = [response] #use sync http mock
        self.real_asynchttpclient.fetch(self.get_url('/'), callback=self.stop, method="POST", body='')
        resp = self.wait()
        print resp.body
    
    def test_asynchttpclient(self):
        request = HTTPRequest('http://google.com')
        response = HTTPResponse(request, 200,
                                buffer=StringIO('some async text'))
        'since http fetch is mocked out, flow isnt transfered to callback, hence create lambda func which wraps the response'
        self.mock_async_client().fetch.side_effect = lambda x,y: y(response) #use async http mock
        self.real_asynchttpclient.fetch(self.get_url('/'), self.stop)
        resp = self.wait()
        print resp.body

application = tornado.web.Application([
        (r'/', TestHandler)])

if __name__ == '__main__':
    unittest.main()

'''    
Sunils-MacBook-Pro:tests sunilmallya$ python test_asynclient.py 
some async text
.some text
.
----------------------------------------------------------------------
Ran 2 tests in 0.021s
OK
'''
