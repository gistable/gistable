#! /usr/bin/python

import smtplib

from optparse import OptionParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

parser = OptionParser()
parser.add_option("-f", "--from", dest="sender", help="sender email address", default="no-reply@doma.in")
parser.add_option("-t", "--to", dest="recipient", help="recipient email address")
parser.add_option("-s", "--subject", dest="subject", help="email subject", default="Default Subject")
parser.add_option("-i", "--image", dest="image", help="image attachment", default=False)
parser.add_option("-p", "--pdf", dest="pdf", help="pdf attachment", default=False)

(options, args) = parser.parse_args()


# Create message container.
msgRoot = MIMEMultipart('related')
msgRoot['Subject'] = options.subject
msgRoot['From'] = options.sender
msgRoot['To'] = options.recipient

# Create the body of the message.
html = """\
    <p>This is an inline image<br/>
        <img src="cid:image1">
    </p>
"""

# Record the MIME types.
msgHtml = MIMEText(html, 'html')

if options.image is not False:
    img = open(options.image, 'rb').read()
    msgImg = MIMEImage(img, 'png')
    msgImg.add_header('Content-ID', '<image1>')
    msgImg.add_header('Content-Disposition', 'inline', filename=options.image)

if options.pdf is not False:
    pdf = open(options.pdf, 'rb').read()
    msgPdf = MIMEApplication(pdf, 'pdf') # pdf for exemple
    msgPdf.add_header('Content-ID', '<pdf1>') # if no cid, client like MAil.app (only one?) don't show the attachment
    msgPdf.add_header('Content-Disposition', 'attachment', filename=options.pdf)
    msgPdf.add_header('Content-Disposition', 'inline', filename=options.pdf)

msgRoot.attach(msgHtml)
msgRoot.attach(msgImg)
msgRoot.attach(msgPdf)

# Send the message via local SMTP server.
s = smtplib.SMTP('localhost')
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
#s.sendmail(options.sender, options.recipient, msgRoot.as_string())
s.sendmail(options.sender, options.recipient, msgRoot.as_string())
s.quit()