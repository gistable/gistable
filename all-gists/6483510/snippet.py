#!/usr/bin/env python
"""
Decrypting proxy for Snapchat

Based on mitmproxy + pysnap

https://github.com/mitmproxy/mitmproxy
https://github.com/martinp/pysnap

"""
import os, cgi, code
from libmproxy import controller, proxy
from pysnap import decrypt, is_video, is_image
from StringIO import StringIO

class SnapSniff(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.count = 1

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def process_snapchat(self, blob):
        data = decrypt(blob)
        filename = ''
        if is_image(data):
            filename = 'snap%s.jpg' % str(self.count).zfill(4)
        elif is_video(data):
            filename = 'snap%s.mp4' % str(self.count).zfill(4)
        if filename:
            f=file(filename,'wb')
            f.write(data)
            f.close()
            print 'Wrote %s (%s bytes)' % (filename,len(data))
            os.system('open %s' % filename)
            self.count+=1

    def handle_request(self, msg):
        hid = (msg.host, msg.port)
        if msg.host == 'feelinsonice-hrd.appspot.com' and msg.path == '/bq/upload':
            env = {}
            env['REQUEST_METHOD'] = msg.method
            env['CONTENT_TYPE'] = msg.get_content_type()
            env['CONTENT_LENGTH'] = len(msg.content)
            c = cgi.parse(environ=env,fp=StringIO(msg.content))
            if c.has_key('username'):
                print 'Upload from %s' % c['username'][0]
                self.process_snapchat(c['data'][0])
        msg.reply()

    def handle_response(self, msg):
        hid = (msg.request.host, msg.request.port)
        if msg.request.host == 'feelinsonice-hrd.appspot.com':
            self.process_snapchat(msg.content)
        msg.reply()

config = proxy.ProxyConfig(
    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
)
port = 3128
server = proxy.ProxyServer(config, port)
m = SnapSniff(server)
print 'Listening on port %s' % port
m.run()
