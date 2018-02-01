"""
Example code for sending emails using boto's SES module. Its main purpose is to
show how easy it is to build multipart text/html emails.

Unfortunately, at this time Amazon's SES doesn't seem to allow you to add
attachments to messages, but if it does in the future it would probably look
like the code that I've commented out below the exception.

The SES module of the Boto package isn't quite finalized yet, but I currently
have this code running using Harry Marr's implementation which is available at:
https://github.com/hmarr/boto/tree/ses
"""

import mimetypes
from email import encoders
from email.utils import COMMASPACE
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from boto.ses import SESConnection


AWS_ACCESS_KEY = 'PUT ACCESS KEY HERE'
AWS_SECRET_KEY = 'PUT SECRET KEY HERE'

connection = SESConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)


class SESMessage(object):
    """
    Usage:
    
    msg = SESMessage('from@example.com', 'to@example.com', 'The subject')
    msg.text = 'Text body'
    msg.html = 'HTML body'
    msg.send()
    
    """
    
    def __init__(self, source, to_addresses, subject, **kw):
        self.ses = connection
        
        self._source = source
        self._to_addresses = to_addresses
        self._cc_addresses = None
        self._bcc_addresses = None

        self.subject = subject
        self.text = None
        self.html = None
        self.attachments = []

    def send(self):
        if not self.ses:
            raise Exception, 'No connection found'
        
        if (self.text and not self.html and not self.attachments) or \
           (self.html and not self.text and not self.attachments):
            return self.ses.send_email(self._source, self.subject,
                                       self.text or self.html,
                                       self._to_addresses, self._cc_addresses,
                                       self._bcc_addresses,
                                       format='text' if self.text else 'html')
        else:
            if not self.attachments:
                message = MIMEMultipart('alternative')
                
                message['Subject'] = self.subject
                message['From'] = self._source
                if isinstance(self._to_addresses, (list, tuple)):
                    message['To'] = COMMASPACE.join(self._to_addresses)
                else:
                    message['To'] = self._to_addresses
                
                message.attach(MIMEText(self.text, 'plain'))
                message.attach(MIMEText(self.html, 'html'))
            else:
                raise NotImplementedError, 'SES does not currently allow ' + \
                                           'messages with attachments.'
#                message = MIMEMultipart()
#                
#                message_alt = MIMEMultipart('alternative')
#                
#                if self.text:
#                    message_alt.attach(MIMEText(self.text, 'plain'))
#                if self.html:
#                    message_alt.attach(MIMEText(self.html, 'html'))
#                
#                message.attach(message_alt)
#                
#                message['Subject'] = self.subject
#                message['From'] = self._source
#                if isinstance(self._to_addresses, (list, tuple)):
#                    message['To'] = COMMASPACE.join(self._to_addresses)
#                else:
#                    message['To'] = self._to_addresses
#                message.preamble = 'You will not see this in a MIME-aware mail reader.\n'

#                print 'message: ', message.as_string()

#                for attachment in self.attachments:
#                    # Guess the content type based on the file's extension.  Encoding
#                    # will be ignored, although we should check for simple things like
#                    # gzip'd or compressed files.
#                    ctype, encoding = mimetypes.guess_type(attachment)
#                    if ctype is None or encoding is not None:
#                        # No guess could be made, or the file is encoded (compressed), so
#                        # use a generic bag-of-bits type.
#                        ctype = 'application/octet-stream'
#                    maintype, subtype = ctype.split('/', 1)
#                    if maintype == 'text':
#                        fp = open(attachment)
#                        # Note: we should handle calculating the charset
#                        part = MIMEText(fp.read(), _subtype=subtype)
#                        fp.close()
#                    elif maintype == 'image':
#                        fp = open(attachment, 'rb')
#                        part = MIMEImage(fp.read(), _subtype=subtype)
#                        fp.close()
#                    elif maintype == 'audio':
#                        fp = open(attachment, 'rb')
#                        part = MIMEAudio(fp.read(), _subtype=subtype)
#                        fp.close()
#                    else:
#                        fp = open(attachment, 'rb')
#                        part = MIMEBase(maintype, subtype)
#                        part.set_payload(fp.read())
#                        fp.close()
#                        # Encode the payload using Base64
#                        encoders.encode_base64(part)
#                    # Set the filename parameter
#                    part.add_header('Content-Disposition', 'attachment', filename=attachment)
#                    message.attach(part)
            
            return self.ses.send_raw_email(self._source, message.as_string(),
                                           destinations=self._to_addresses)