# -*- encoding: UTF-8 -*-

import smtplib
import json
from email.mime.text import MIMEText

MAILGUN_SMTP_LOGIN = "postmain@revolunet.mailgun.org"
MAILGUN_SMTP_PASSWORD = "secret"

def send_message_via_smtp(from_, to, mime_string):
    ''' sends a mime message to mailgun SMTP gateway '''
    smtp = smtplib.SMTP("smtp.mailgun.org", 587)
    smtp.login(MAILGUN_SMTP_LOGIN, MAILGUN_SMTP_PASSWORD)
    smtp.sendmail(from_, to, mime_string)
    smtp.quit()


def send_mailgun_message(from_, to, subject, text, tag=None, variables={}, track=True):
    ''' compose and sends a text-only message through mailgun '''

    msg = MIMEText(text, _charset='utf-8')

    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = to
    if tag:
        # you can attach tags to your messages
        msg['X-Mailgun-Tag'] = tag
    if track:
        # you can auto transform links to track clicks
        msg['X-Mailgun-Track'] = "yes"
        if variables:
            # you can embed data in the email, will be passed to your webhook
            msg['X-Mailgun-Variables'] = json.dumps(variables)

    send_message_via_smtp(from_, to, msg.as_string())


if __name__ == '__main__':
    text = u"""Hi from mailgun !

I'm testing the API

The tracking links : http://revolunet.com

Works like a charm :)"""

    user_data = {
        'id': 12345,
        'source': '/some/random/info'
    }

    send_mailgun_message('ju@revolunet.com', 'test@revolunet.com', 'Mailgun SMTP test', text, tag='tests', variables=user_data)
