# Found most ofthis at http://ryrobes.com/python/python-snippet-sending-html-email-with-an-attachment-via-google-apps-smtp-or-gmail/
# Adapted to accept a list of files for multiple file attachments
# From other stuff I googled, a little more elegant way of converting html to plain text
# This works in 2.7 and my brain gets it.

######### Setup your stuff here #######################################

attachments = ['test_pdf.pdf', 'test_waiver.pdf']

username = 'joe@gmail.com'
password = 'j0ej0e'
host = 'smtp.gmail.com:587' # specify port, if required, using this notations

fromaddr = 'joe@rogers.com' # must be a vaild 'from' address in your GApps account
toaddr  = 'joe@gmail.com'
replyto = fromaddr # unless you want a different reply-to

msgsubject = 'This is the subject of the email! WooHoo!'

htmlmsgtext = """<h2>This is my message body in HTML...WOW!!!!!</h2>
                <p>\
                 Hey, Hey, Ho, Ho, got a paragraph here. A lovely paragraph it is.\
                 You've never seen a better paragraph than this.\
                 I make some of the best paragraphs you have ever seen.\
                 Hey, Hey, Ho, Ho, got a paragraph here. A lovely paragraph it is.\
                 You've never seen a better paragraph than this.\
                 I make some of the best paragraphs you have ever seen.\                 
                 </p>
                <ul>
                    <li>This is a list item</li>
                    <li>This is another list item</li>
                    <li>And yet another list item, pretty big list</li>
                    <li>OMG this is a long list!</li>
                </ul>
                <p><strong>Here are your attachments:</strong></p><br />"""

######### In normal use nothing changes below this line ###############

import smtplib, os, sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from HTMLParser import HTMLParser

# A snippet - class to strip HTML tags for the text version of the email

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

########################################################################

try:
    # Make text version from HTML - First convert tags that produce a line break to carriage returns
    msgtext = htmlmsgtext.replace('</br>',"\r").replace('<br />',"\r").replace('</p>',"\r")
    # Then strip all the other tags out
    msgtext = strip_tags(msgtext)

    # necessary mimey stuff
    msg = MIMEMultipart()
    msg.preamble = 'This is a multi-part message in MIME format.\n'
    msg.epilogue = ''

    body = MIMEMultipart('alternative')
    body.attach(MIMEText(msgtext))
    body.attach(MIMEText(htmlmsgtext, 'html'))
    msg.attach(body)

    if 'attachments' in globals() and len('attachments') > 0: # are there attachments?
        for filename in attachments:
            f = filename
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

    msg.add_header('From', fromaddr)
    msg.add_header('To', toaddr)
    msg.add_header('Subject', msgsubject)
    msg.add_header('Reply-To', replyto)

    # The actual email sendy bits
    server = smtplib.SMTP(host)
    server.set_debuglevel(False) # set to True for verbose output
    try:
        # gmail expect tls
        server.starttls()
        server.login(username,password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print 'Email sent'
        server.quit() # bye bye
    except:
        # if tls is set for non-tls servers you would have raised an exception, so....
        server.login(username,password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print 'Email sent'
        server.quit() # sbye bye        
except:
    print ('Email NOT sent to %s successfully. %s ERR: %s %s %s ', str(toaddr), 'tete', str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2]) )
    #just in case
