#!/usr/bin/env python
"""
    Inject inverting css
    Usage:
        inverted_internet
"""
from libmproxy import controller, proxy
import os
import sys


class InjectingMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_response(self, msg):
        if msg.content:
            c = msg.replace('</body>', '<style>body {transform:rotate(180deg);-ms-transform:rotate(180deg);-webkit-transform:rotate(180deg);}</style></body>')
            if c > 0:
                print 'CSS injected!'
        msg.reply()


def main(argv):
    config = proxy.ProxyConfig(
        cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
    )
    server = proxy.ProxyServer(config, 8080)
    print 'Starting proxy...'
    m = InjectingMaster(server)
    m.run()

if __name__ == '__main__':
    main(sys.argv)
