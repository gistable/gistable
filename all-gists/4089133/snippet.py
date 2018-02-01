#!/usr/bin/env python

"""
Rudimentary Spotify Web Proxy using mitmproxy.
Use it by your own responsibility!!
This was only entertainment!!
"""

import random
import hashlib

from libmproxy import proxy, flow


class SpotifyProxy(flow.FlowMaster):
    def run(self):
        try:
            flow.FlowMaster.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, r):
        f = flow.FlowMaster.handle_request(self, r)
        if f:
            r._ack()
        return f

    def handle_response(self, r):
        f = flow.FlowMaster.handle_response(self, r)
        if f:
            r._ack()
        if 'cloudfront.net' in f.request.host and 'mp3' in f.request.path:
            filename = '%s.mp3' % hashlib.sha1(str(random.random())).hexdigest()
            mp3 = open(filename, 'w')
            mp3.write(f.response.content)
            mp3.close()
            print "Saved to %s" % filename
        return f

config = proxy.ProxyConfig()
state = flow.State()
server = proxy.ProxyServer(config, 9000)
m = SpotifyProxy(server, state)
m.run()
