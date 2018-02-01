# smspython.py
# Sends sms message to any cell phone using gmail smtp gateway
# Written by Alex Le (http://alexanderle.com)

import smtplib, base64, sys, re

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

MAX_TEXT_LENGTH = 160

SmsGateways = [
   'tmomail.net',             # tmobile
   'mms.att.net',             # at&t
   'vtext.com',               # verizon
   'page.nextel.com',         # sprint
   'sms.mycricket.com',       # cricket 
   'vmobl.com',               # virgin mobile US
   'sms.myboostmobile.com'    # boost mobile
]

def LogInSMTPServer( email, password ):
   server = smtplib.SMTP( "smtp.gmail.com", 587 )
   server.starttls()
   server.login( email, password )

   return server

def SendSMS( server, phone, msg_text, attach_file ):

   if len( msg_text ) <= MAX_TEXT_LENGTH:

      # Send to all gateways, since a phone number
      # can only be specific to one carrier.
      for gateway in SmsGateways:
         destination = phone + '@' + gateway

         msg = MIMEMultipart()
         msg.attach( MIMEText(msg_text, 'plain') )

         # Check if valid attachment
         if attach_file != '':
            fp = open( attach_file, 'rb' )
            msg_img = MIMEImage( fp.read() )
            fp.close()

            msg.attach( msg_img )

         server.sendmail( '', destination, msg.as_string() )

   else:
      print 'Message is too long. SMS not sent.'

   server.quit()

#### Main Program ####
fo = open( 'sms_info.txt', 'r' )

# Read sensitive information from external file
email = fo.readline().rstrip('\n')
password = base64.b64decode( fo.readline().rstrip('\n') )

p = re.compile( '\d{10}' )

# Get destination phone number
phone = raw_input( 'Enter 10 digit phone number: ' )
if p.match( phone ) == None:
   print 'Valid phone not entered!'
   sys.exit(0)

# Get message
msg_text = raw_input( 'Enter message: ' )

# Ask for attachments
attach_file = raw_input( 'Enter attachments: ')

print '\nLogging into SMTP server..'
smtp_server = LogInSMTPServer( email, password )

SendSMS( smtp_server, phone, msg_text, attach_file )
print 'SMS sent to %s' % phone

