#!/usr/bin/python

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

gmail_user = "email@example.com"
gmail_pwd = "password"
from_gmail_user = "Social Register <email@example.com>"

def mail(to, subject, text, cc=None, bcc=None, reply_to=None, attach=None,
         html=None, pre=False, custom_headers=None):
    msg = MIMEMultipart()

    msg['From'] = from_gmail_user
    msg['To'] = to
    msg['Subject'] = subject

    to = [to]

    if cc:
        # cc gets added to the text header as well as list of recipients
        if type(cc) in [str, unicode]:
            msg.add_header('Cc', cc)
            cc = [cc]
        else:
            cc = ', '.join(cc)
            msg.add_header('Cc', cc)
        to += cc

    if bcc:
        # bcc does not get added to the headers, but is a recipient
        if type(bcc) in [str, unicode]:
            bcc = [bcc]
        to += bcc

    if reply_to:
        msg.add_header('Reply-To', reply_to)

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to
    # display.

    if pre:
        html = "<pre>%s</pre>" % text
    if html:
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)

        msgText = MIMEText(text)
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it
        # below
        msgText = MIMEText(html, 'html')
        msgAlternative.attach(msgText)
    else:
        msg.attach(MIMEText(text))

    if attach:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attach, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(attach))
        msg.attach(part)

    if custom_headers:
        for k, v in custom_headers.iteritems():
            msg.add_header(k, v)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)

    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
