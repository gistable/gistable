#!/usr/bin/python
#@author Bommarito Consulting, LLC; http://bommaritollc.com
#@date 2012-12-20

import subprocess
import smtplib
from email.mime.text import MIMEText

fromAddress = 'root@bommaritollc.com'
adminEmail = 'michael@bommaritollc.com'

def sendMessage(emailAddress, errorBuffer):
    msg = MIMEText("MySQL down.\nError: " + errorBuffer)
    msg['Subject'] = 'BCLLC MySQL Down'
    msg['From'] = fromAddress
    msg['To'] = emailAddress
    s = smtplib.SMTP('localhost')
    s.sendmail(fromAddress, emailAddress, msg.as_string())

def main():
    statusProc = subprocess.Popen(['mysqladmin', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outputBuffer = statusProc.stdout.read().strip()
    errorBuffer = statusProc.stderr.read().strip()

    if 'uptime' not in outputBuffer.lower() or len(errorBuffer) > 0:
        sendMessage(adminEmail, errorBuffer)

if __name__ == "__main__":
    main()
