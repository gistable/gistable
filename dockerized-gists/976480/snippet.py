# -*- coding: utf-8 -*-
"""
    amazon_sender.py
    ~~~~~~~~

    Python helper class that can send emails using Amazon SES and boto.
    The biggest feature of this class is that encodings are handled properly.
    It can send both text and html emails.
    This implementation is using Python's standard library (which opens up for a lot more options).

    Example::

        amazon_sender = AmazonSender(AWS_ID, AWS_SECRET)

        amazon_sender.send_email(sender=u'朋友你好 <john@doe.com>',
                                 to='blah@blah.com',
                                 subject='Hello friend',
                                 text='Just a message',
                                 html='<b>Just a message</b>',
                                 sender_ascii='Ascii Sender <no_reply@wedoist.com>')


    :copyright: 2011 by Amir Salihefendic ( http://amix.dk/ ).
    :license: BSD
"""

import types

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE

from boto.ses import SESConnection


class AmazonSender(object):

    client = None

    def __init__(self, aws_key, aws_secret):
        self.aws_key = aws_key
        self.aws_secret = aws_secret

    def send_email(self, sender,
                         to_addresses,
                         subject,
                         text,
                         html=None,
                         reply_addresses=None,
                         sender_ascii=None):
        if not sender_ascii:
            sender_ascii = sender

        client = self.get_client()

        message = MIMEMultipart('alternative')
        message.set_charset('UTF-8')

        message['Subject'] = _encode_str(subject)
        message['From'] = _encode_str(sender)

        message['To'] = _convert_to_strings(to_addresses)

        if reply_addresses:
            message['Reply-To'] = _convert_to_strings(reply_addresses)

        message.attach(MIMEText(_encode_str(text), 'plain'))

        if html:
            message.attach(MIMEText(_encode_str(html), 'html'))

        return client.send_raw_email(sender_ascii, message.as_string(),
                                                   destinations=to_addresses)

    def vertify_email(self, email):
        client = self.get_client()
        return client.verify_email_address(email)

    def get_client(self):
        if not self.client:
            self.client = SESConnection(self.aws_key,
                                        self.aws_secret)
        return self.client


#--- Helpers ----------------------------------------------
def _convert_to_strings(list_of_strs):
    if isinstance(list_of_strs, (list, tuple)):
        result = COMMASPACE.join(list_of_strs)
    else:
        result = list_of_strs
    return _encode_str(result)

def _encode_str(s):
    if type(s) == types.UnicodeType:
        return s.encode('utf8')
    return s