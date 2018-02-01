#!/usr/bin/python
import string, time, calendar, hashlib, urllib2, smtplib
from email.mime.text import MIMEText

# Cydia globals
product_ids = ['org.thebigboss.somepackage', 'org.thebigboss.someotherpackage']
splits = [ 0.70, 0.35 ]
vendor_id = ""
vendor_secret = ""

# SMTP globals
smtp_server = "smtp.gmail.com"
smtp_username = "username@gmail.com"
smtp_password = "password"
smtp_email = smtp_username

def main():
    vendor_hash = hashlib.md5()
    vendor_hash.update(vendor_id)
    vendor_hash.update(vendor_secret)
    vendor_hash = vendor_hash.hexdigest()

    money_made = 0.00

    time_cutoff = time.time() - (24 * 60 * 60)

    for (product_id, split) in zip(product_ids, splits):

        failureCount = 0
        while True:
            try:
                transactions = urllib2.urlopen('http://cydia.saurik.com/api/roster?package=' + product_id + '&vendor-hash=' + vendor_hash)
            except:
                failureCount += 1
                if failureCount >= 5:
                    raise
            else:
                break

        transaction = transactions.readline()

        while transaction:
            pieces = transaction.split(" ")

            price = float(pieces[8]) * split

            date = string.join(pieces[3:5], " ")
            date = date.split(".")
            date = string.join(date[:1])
            date = time.strptime(date, "%Y-%m-%d %H:%M:%S")

            if calendar.timegm(date) > time_cutoff:
                money_made += price
            else:
                break

            transaction = transactions.readline()

    money_made = '%.2f' % money_made

    msg = MIMEText("You made $" + money_made + " from the Cydia Store yesterday.")
    msg['Subject'] = "Cydia Store Report"
    msg['From'] = smtp_email
    msg['To'] = smtp_email

    smtp_client = smtplib.SMTP_SSL(smtp_server, 465)
    smtp_client.login(smtp_username, smtp_password)
    smtp_client.sendmail(smtp_email, [smtp_email], msg.as_string())
    smtp_client.quit()

if __name__ == "__main__":
    main()
