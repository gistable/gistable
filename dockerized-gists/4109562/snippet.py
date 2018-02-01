#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sleekxmpp
import subprocess
import time

class TWBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, whitelist):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.whitelist = whitelist

        self.add_event_handler("session_start", self.on_start)
        self.add_event_handler("message", self.handle_message)

    def on_start(self, event):
        self.send_presence()
        self.get_roster()

    def handle_message(self, msg):
        if msg['type'] in ('chat', 'normal') and ((str)(msg["from"])).split("/")[0] in self.whitelist:
            msg.reply(self.exec_taskwarrior(msg["body"])).send()

    def exec_taskwarrior(self, arguments):
        commands = ["task", "rc.confirmation=off", "rc.verbose=no", "rc.bulk=1000"]
        commands = commands + arguments.split(' ')
        process = subprocess.Popen(commands, stdout=subprocess.PIPE)

        return process.stdout.read().rstrip()

if __name__ == '__main__':
    # FIXME: Not sure how spoof-proof XMPP is. Is this whitelist enough?
    whitelist = ["allowed_user@example.com", "second_user@example.com"]
    
    xmpp = TWBot("bot@example.com/bot", "password", whitelist)
    
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    xmpp.connect()
    xmpp.process(block=True)