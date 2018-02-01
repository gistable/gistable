gmail_username = 'username@gmail.com'
recipients = 'recipient@example.com'
# https://en.wikipedia.org/wiki/List_of_SMS_gateways
# 10DigitNumber@text.att.net for AT&T
# 10DigitNumber@vtext.com for Verizon
 
from email.mime.text import MIMEText
msg = MIMEText('This is the body of the message.')
msg['Subject'] = 'Blank subject lines look like spam.'
msg['From'] = gmail_username
msg['To'] = recipients
msg = msg.as_string()
 
import smtplib
session = smtplib.SMTP('smtp.gmail.com', 587)
session.ehlo()
session.starttls()
session.login(gmail_username, 'your-gmail-or-application-specific-password')
session.sendmail(gmail_username, recipients, msg)
session.quit()