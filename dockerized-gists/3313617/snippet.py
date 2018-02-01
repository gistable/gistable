#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""

        First test in terminal

        ./sendsms mikko "Test msg"

        Then connect to Zabbix

        - Add Twilio media in Administration

        - Bound media to your user in User -> Media

        - To Send to add "mikko"


"""
# easy_install-2.7 twilio
from twilio.rest import TwilioRestClient

import sys

def send(to, msg):

    # no white space in numbers!
    contacts = {
        "mikko": "+123123",
        "pete": "+12123"
    }

    if to in contacts:
        account = "tttt"
        token = "yyyy"
        client = TwilioRestClient(account, token)
        twilionumber = "+123123"

        message = client.sms.messages.create(to=contacts[to], from_=twilionumber, body=msg)

        #print message

if __name__ == "__main__":

    if len(sys.argv) > 2:
        to = sys.argv[1]
        msg = sys.argv[2]

        send(to, msg)
    else:
        print "Usage: %s to msg" % sys.argv[0]