"""
Context manager or function to send text messages to your phone when a
process is done.

Edit the global variables. You might be able to find your phone e-mail 
address here: http://tinywords.com/about-old/mobile/

Usage:
with SendText("long running process"):
    do_something()
"""

import smtplib
from email.MIMEText import MIMEText
import time
import getpass

# global configuration
email_from = ''.join(['user.name', 'AT', 'gmail', '.com']).replace('AT','@')
email_to = ''.join(['###########', 'AT', 'mobile.mycingular.com']).replace('AT','@')
subject = 'My Project'
from_whom = 'My Project'


def send_text(process, pwd, elapsed=None):
    message = "Done running %s" % process
    if elapsed:
        message += "\nElapsed: %s" % elapsed
    subject = message
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_whom
    msg['To'] = email_to

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_from, pwd)
    server.sendmail(email_from, email_to, msg.as_string())
    server.close()

class SendText(object):
    def __init__(self, process):
        self.process = process

    def __enter__(self):
        self.pwd = getpass.getpass("Gmail password: ")
        self.tic = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        toc = time.time()
        elapsed = round(toc-self.tic,2)
        print "Elapsed: %f seconds" % elapsed
        try: # catch an error so result still passes through
            send_text(self.process, self.pwd, elapsed)
        except:
            print "Sending text failed"