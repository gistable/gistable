#!/usr/bin/env python3

# Joonas Kuorilehto 2013
# This script is Public Domain.

import csv
import subprocess
import pipes
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

EMAIL = **************
ADB_BINARY = "adt-bundle-linux-x86_64/sdk/platform-tools/adb"
SMS_DB = "/data/data/com.android.providers.telephony/databases/mmssms.db"

def android_sql(sql_query):
    cmd = 'sqlite3 -csv -header %s %s' % (SMS_DB, pipes.quote(sql_query))
    shell_cmd = 'su -c {}'.format(pipes.quote(cmd))
    p = subprocess.Popen([ADB_BINARY, 'shell', shell_cmd],
            stdout=subprocess.PIPE, universal_newlines=True)
    sqlite_out, sqlite_stderr = p.communicate()
    reader = csv.DictReader(sqlite_out.split("\n"))
    return reader

def get_unread_messages():
    # Format message; get unread SMS messages from Android
    result = android_sql("SELECT _id, address, date, body FROM sms WHERE read=0;")
    message_ids = []
    email_message = ""
    for msg in result:
        message_ids.append(msg['_id'])
        date = datetime.fromtimestamp(int(int(msg['date'])/1000))
        m = "{} [{}]\n  {}\n\n".format(date, msg['address'], msg['body'])
        email_message += m
    return (message_ids, email_message)

def send_email(message_content, sender=EMAIL, to=EMAIL,
        subject="Received SMS messages", charset="UTF-8"):
    # Create a text/plain message
    msg = MIMEText(message_content.encode(charset), _charset=charset)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

def main():
    message_ids, email_message = get_unread_messages()
    if len(message_ids) > 0:
        send_email(email_message)
        read_ids = ",".join(message_ids)
        android_sql("UPDATE sms SET read=1 WHERE _id in ({});".format(read_ids))

if __name__ == '__main__':
    main()
