import webapp2
from twilio import twiml
from twilio.rest import TwilioRestClient
 
class SendSMS(webapp2.RequestHandler):
    def get(self):
        # replace with your credentials from: https://www.twilio.com/user/account
        account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        auth_token = "xxxxxxxxxxxxxxxxxxxxxxxxxx"
        client = TwilioRestClient(account_sid, auth_token)
        # replace "to" and "from_" with real numbers
        rv = client.sms.messages.create(to="+14155551212",
                                        from_="+14085551212",
                                        body="Hello Monkey!")
        self.response.write(str(rv))
 
app = webapp2.WSGIApplication([('/send_sms', SendSMS)],
                              debug=True)