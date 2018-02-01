#!/usr/bin/env python
import smtplib
from email.mime.text import MIMEText

USERNAME = "username@gmail.com"
PASSWORD = "password"
MAILTO  = "mailto@gmail.com"

msg = MIMEText('This is the body of the email')
msg['Subject'] = 'The email subject'
msg['From'] = USERNAME
msg['To'] = MAILTO

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo_or_helo_if_needed()
server.starttls()
server.ehlo_or_helo_if_needed()
server.login(USERNAME,PASSWORD)
server.sendmail(USERNAME, MAILTO, msg.as_string())
server.quit()