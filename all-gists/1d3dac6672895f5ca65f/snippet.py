__author__ = 'srv'

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

username = ''  # Email Address from the email you want to send an email
password = ''  # Password
server = smtplib.SMTP('')

"""
SMTP Server Information
1. Gmail.com: smtp.gmail.com:587
2. Outlook.com: smtp-mail.outlook.com:587
3. Office 365: outlook.office365.com
Please verify your SMTP settings info.
"""

# Create the body of the message (a HTML version for formatting).
html = """Add you email body here"""


# Function that send email.
def send_mail(username, password, from_addr, to_addrs, msg):
    server = smtplib.SMTP('smtp-mail.outlook.com', '587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(from_addr, to_addrs, msg.as_string())
    server.quit()

# Read email list txt
email_list = [line.strip() for line in open('email.txt')]

for to_addrs in email_list:
    msg = MIMEMultipart()

    msg['Subject'] = "Hello How are you ?"
    msg['From'] = from_addr
    msg['To'] = to_addrs

    # Attach HTML to the email
    body = MIMEText(html, 'html')
    msg.attach(body)

    # Attach Cover Letter to the email
    cover_letter = MIMEApplication(open("file1.pdf", "rb").read())
    cover_letter.add_header('Content-Disposition', 'attachment', filename="file1.pdf")
    msg.attach(cover_letter)

    # Attach Resume to the email
    cover_letter = MIMEApplication(open("file2.pdf", "rb").read())
    cover_letter.add_header('Content-Disposition', 'attachment', filename="file2.pdf")
    msg.attach(cover_letter)

    try:
        send_mail(username, password, from_addr, to_addrs, msg)
        print "Email successfully sent to", to_addrs
    except SMTPAuthenticationError:
        print 'SMTPAuthenticationError'
        print "Email not sent to", to_addrs