#!/usr/bin/env python
#! -*- coding:utf-8 -*-
"""
Mail to Slack
==========
A Simple SMTP server that will forward messages to Slack. It provides a simple
authentication mechanism via reciever's domain. This utility is designed for
monit monitoring.
"""
import email
import smtpd
import asyncore
import httplib
import json
import os

from argparse import ArgumentParser
from multiprocessing import Process

SLACK_HOST = "hooks.slack.com"
SLACK_PATH = "/services/*****************" # Slack Token 

def sendmessage(channel, message):
    outdata = dict()
    outdata['channel'] = "#"+channel
    outdata['text'] = message
    outs = json.dumps(outdata)
    headers = {'Content-Type': 'application/json'}
    conn = httplib.HTTPSConnection(SLACK_HOST)
    conn.request("POST", SLACK_PATH, outs, headers)
    resp = conn.getresponse()
    conn.close()
    if resp.status == 200:
        return True
    print resp.status, resp.reason
    return False
    
class Mail2Slack(smtpd.SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data):
        room = rcpttos[0].split("@")[0]
        content = email.Parser.Parser().parsestr(data)
        sendmessage(room, content['Subject'] + content.get_payload().strip())

def main_daemon(port):
    server = Mail2Slack(('127.0.0.1', args.port), None)
    asyncore.loop()
        
def main():
    parser = ArgumentParser(description="A mail server that forward everything to slack")
    parser.add_argument("--port", dest="port", type=int, default=2025,
                        help="Custom dictionary")
    parser.add_argument("--pidfile", dest="pidfile", type=str, default=None,
                        help="Path to pidfile")
    args = parser.parse_args()
    server = Process(target=main_daemon, args=(args.port,))
    server.daemon = True
    server.start()
    if args.pidfile is not None:
        pidfile = open(args.pidfile, 'w')
        pidfile.write("%d" % server.pid)
        pidfile.close()

if __name__ == "__main__":
    main()