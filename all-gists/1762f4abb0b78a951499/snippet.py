#!/usr/bin/env python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
 
mail_user = "email@yourdomain.org"
mail_pwd = "password"
SMTP_HOST = "smtp.yourdomain.org"
#True or False
SMTP_SSL = True 
 
 
def mail(to, subject, text):
    msg = MIMEMultipart()
    msg['From'] = mail_user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    if SMTP_SSL:
        mail_server = smtplib.SMTP_SSL(SMTP_HOST)
    else:
        mail_server = smtplib.SMTP(SMTP_HOST)
        mail_server.starttls()
    mail_server.ehlo()
    mail_server.login(mail_user, mail_pwd)
    mail_server.sendmail(mail_user, to, msg.as_string())
    mail_server.close()
 
if __name__ == '__main__':
 
    if len(sys.argv) == 4:
        mail(
            to=sys.argv[1],
            subject=sys.argv[2],
            text=sys.argv[3]
        )
    else:
        print u"zabbix-smtp.py to subject text"