'''
Nexus Notification Script

This script searches for the specific button in the Google Play store that appears
when the phone is in stock and you are able to buy it. It will send you an email
as a notification.

written by: Marco A Morales
http://www.marcoamorales.com
'''

import smtplib
import requests
import datetime
 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER = 'xxxxxxxxxxx@gmail.com'
PASSWORD = 'xxxxxxxxxxxxx'

test_url = 'http://www.google.com'
test_search_pattern = 'google'

# This URL is for the 16GB version.
url = 'https://play.google.com/store/devices/details?id=nexus_4_16gb'
search_pattern = 'buy-hardware-form'

def check_nexus(url, search_pattern):
    r = requests.get(url)
    if r.text.find(search_pattern) != -1:
        print 'NEXUS FOUND!'
        send_mail(SMTP_SERVER, SMTP_PORT, SENDER, PASSWORD)
    else:
        print 'Nothing found: ' + str(datetime.datetime.now())

def send_mail(smtp_server, smtp_port, sender, password):
    subject = 'NEXUS FOUND'
    body = 'Your script has found a Nexus 4 Device in the Google Play Store.'

    # I send an email from me to me, so I use the same email for sender and recipient
    headers = ["From: " + sender,
           "Subject: " + subject,
           "To: " + sender,
           "MIME-Version: 1.0",
           "Content-Type: text/html"]
    headers = "\r\n".join(headers)
    session = smtplib.SMTP(smtp_server, smtp_port)

    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)

    session.sendmail(sender, sender, headers + "\r\n\r\n" + body)
    session.quit()

def main():
    check_nexus(url, search_pattern)

if __name__ == '__main__':
    main()
