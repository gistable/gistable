import getpass
import csv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import xlrd
import xlwt
import re
from time import sleep

def mail(to, subject, text, gmail_user, gmail_pwd):
    msg = MIMEMultipart()
    
    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject
    
    msg.attach(MIMEText(text))
    

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
    print "Email sent to %s" % to
    


gmail_addr = raw_input("Email account to send from: ")
password = getpass.getpass("Enter your password (will not be stored): ")
subject = raw_input("Subject: ")
filename = raw_input("What file is the list of emails (mailmerge.xls)? ")
if not filename: filename = "mailmerge.xls"

message_file = raw_input("What file is the message file (message.txt)? ")
if not message_file: message_file = "message.txt"
f = open(message_file, "r")
message_text = ''.join(f.readlines())
f.close()

#xls version
if str(filename).endswith(".xls") or str(filename).endswith(".xlsx"):
    nicknames = []
    emails = []
    #open up the workbook
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(0) 

    #check all the rows
    for row_number in xrange(1, sheet.nrows):
        nickname = sheet.cell_value(row_number, 0)
        email = sheet.cell_value(row_number, 1)

        if nickname and email and re.match(r"[^@]+@[^@]+\.[^@]+", email):
            nicknames.append(nickname)
            emails.append(email)


# #csv version
elif str(filename).endswith(".csv"):
    nicknames = []
    emails = []
    emailsReader = csv.reader(open(filename, 'rU'), delimiter=',', quotechar='"')
    skipFlag = True
    for row in emailsReader:
        if not skipFlag:
            try:
                nickname = row[0]
                email = row[1]
                if nickname and email and re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    nicknames.append(nickname)
                    emails.append(email)
            except IndexError:
                continue
        else: skipFlag = False
    #filter out the blank items in the lists of the CSV files
    emails = filter(None, emails)
    nicknames = filter(None, nicknames)
else:
    print "File Format not recognized, accepted types are .csv, .xls, .xlsx"

print "Starting Mail Merge..."

counter = 0
for email in emails:
    GREETING = "%s,\n\n" % nicknames[counter]
    mail(email,
    subject,
    GREETING+message_text,
    gmail_addr,
    password)
    counter += 1
    sleep(1)
    
print "Done sending emails"