#!/usr/bin/env python
# Twilio Tools for Reminding & Calling
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import TwilioRestClient
from twilio import twiml
from flask import Flask

app = Flask(__name__)

account = "TWILIO ACCOUNT"
token = "TWILIO TOKEN"
client = TwilioRestClient(account, token)
child = "+16265551760"
mom = "+16265556498"
ec2_url = "ec2-000-00-00-00.us-west-1.compute.amazonaws.com"

def call_mom():
    call = client.calls.create(to=child, 
                           from_=mom, 
                           url="http://%s/respond" % ec2_url,
                           method='GET')

@app.route("/respond")
def respond():
    r = twiml.Response()
    r.say("You should talk to your mom.")
    with r.gather(action="http://%s/connect" % ec2_url, timeout=15, method='GET') as g:
        g.say('Press 1 followed by the pound key to continue connecting.')
    return str(r)

@app.route("/connect")
def connect():
    r = twiml.Response()
    with r.dial(caller_id=child) as d:
        d.number(mom)
    return str(r)

if __name__ == '__main__':
    call_mom()
    app.run(host="0.0.0.0", port=80, debug=True)
