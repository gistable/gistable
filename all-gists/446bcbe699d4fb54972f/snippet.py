#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
from pyOSC import OSC
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer


# arguments
parser = argparse.ArgumentParser(description='Websocket to OSC bridge')
parser.add_argument('websocket',
                    type=int,
                    nargs='?',
                    default=7776,
                    help='The port for WebSocket')

parser.add_argument('osc',
                    type=int,
                    nargs='?',
                    default=7777,
                    help='The port for OSC')


class OscBridge(WebSocket):
    ''' Websocket to OSC bridge '''

    def __init__(self, server, sock, address):
        super(OscBridge, self).__init__(server, sock, address)

        args = parser.parse_args()
        self.oscClient = OSC.OSCClient()
        self.oscClient.connect(('127.0.0.1', args.osc))

    def parseMsg(self, address, msg):
        messages = []
        if isinstance(msg, dict):
            [messages.extend(self.parseMsg(address + '/' + k, v))
             for k, v in msg.items()]

        elif isinstance(msg, list):
            if isinstance(msg[0], dict) or isinstance(msg[0], list):
                [messages.extend(self.parseMsg(address, m)) for m in msg]
            else:
                messages.append(self.createOsc(address, msg))
        else:
            messages.append(self.createOsc(address, [msg]))
        return messages

    def createOsc(self, address, params):
        msg = OSC.OSCMessage(address)
        [msg.append(param) for param in params]
        return msg

    def handleMessage(self):
        msg = json.loads(self.data)

        oscMsgs = []
        [oscMsgs.extend(self.parseMsg('/' + address, msg))
         for address, msg in msg.items()]

        bundle = OSC.OSCBundle()
        [bundle.append(osc) for osc in oscMsgs]
        self.oscClient.send(bundle)
        print(oscMsgs)

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'


if __name__ == '__main__':
    args = parser.parse_args()

    server = SimpleWebSocketServer('', args.websocket, OscBridge)
    server.serveforever()
