# -*- coding: utf-8 -*-
"""
    IPN Engine
    ~~~~~~~~~~

    PayPal's Instant Payment Notification (IPN) helps integrate PayPal more
    deeply into your web application.  When activated, PayPal will send a
    POST request to a specified URL when a transaction's status changes.

    The most obvious use is to trigger a state change, enable an account,
    download, or trigger an email when a payment is made.
    
    To validate PayPals POST data, the data must be sent back to PayPal
    in exactly the same order, prefixed with 'cmd=_notify-validate'. If
    valid PayPal responds with 'VERIFIED' if not it returns 'INVALID'.

    Requires: flask, requests

"""

from flask import Flask, request
import requests
from werkzeug.datastructures import ImmutableOrderedMultiDict

app = Flask(__name__)

@app.route('/ipn',methods=['POST'])
def ipn():

    arg = ''
    #: We use an ImmutableOrderedMultiDict item because it retains the order.
    request.parameter_storage_class = ImmutableOrderedMultiDict()
    values = request.form
    for x, y in values.iteritems():
        arg += "&{x}={y}".format(x=x,y=y)

    validate_url = 'https://www.sandbox.paypal.com' \
                   '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
                   .format(arg=arg)
                  
    print 'Validating IPN using {url}'.format(url=validate_url)

    r = requests.get(validate_url)

    if r.text == 'VERIFIED':
        print "PayPal transaction was verified successfully."
        # Do something with the verified transaction details.
        payer_email =  request.form.get('payer_email')
        print "Pulled {email} from transaction".format(email=payer_email)
    else:
         print 'Paypal IPN string {arg} did not validate'.format(arg=arg)

    return r.text

if __name__ == '__main__':
    app.debug = True
    app.run("127.0.0.1",5000)