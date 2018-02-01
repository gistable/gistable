# pip install pypdf2
# Thanks to sphilp for updates

########
# USAGE:
########
# You will need to enter your email creds so you can receive the bonus statements
# which you can then review, edit, and forward (sending directly could be dangerous)
#
# This is pigging backing on gmail's API to send the email to yourself
# you will likely have to disable the "secure apps" setting on
# your gmail account to get this to work:
# https://www.google.com/settings/security/lesssecureapps
#
# If you use 2FA on your gmail account then you will alternatively have to set 
# up an "app password", use the generated password in place of your regular password
# https://support.google.com/accounts/answer/185833
#
# Remember to turn it back on after you send the emails
#
# After you're set up simply run $ python split.py path-to-bonus.pdf

import sys
import re
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.mime.application import MIMEApplication

from PyPDF2 import PdfFileWriter, PdfFileReader


# Fill these out
mozilla_address = ""
gmail_address = ""
gmail_username = ""
gmail_password = ""

def split(file_):
    input1 = PdfFileReader(open(file_, "rb"))
    pages = input1.getNumPages()
    for i in range(pages):
        name = extract_name(input1.getPage(i))
        quarter = extract_quarter(input1.getPage(i))
        output = PdfFileWriter()
        filename = "%s_Bonus_Statement_%s.pdf" % (name.replace (" ", "_"), quarter.replace (" ", "_"))

        print "Writing pdf for %s" % name
        outputStream = file(filename, "wb")
        output.addPage(input1.getPage(i))
        output.write(outputStream)
        outputStream.close()

        print "Sending email for %s" % name
        send_email(name, quarter, filename)

def extract_name(page_):
    page_content = page_.extractText()
    name = (page_content.split(':')[0]).split('2017')[1]
    return name

def extract_quarter(page_):
    page_content = page_.extractText()
    quarter = re.findall(r'[Q][\d][ ][\d]+', page_content)
    return quarter[0]

def send_email(name_, quarter_, filename_):
    first_name = name_.split(" ")[0]

    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = mozilla_address
    msg['Subject'] = "%s bonus statement for %s" % (quarter_, name_)
    msg.attach(MIMEText("Hey %s, attached is your bonus statement for %s. Congrats!" % (first_name, quarter_)))

    msg.attach(MIMEApplication(
                open(filename_, 'rb').read(),
                Content_Disposition='attachment; filename="%s"' % filename_,
                Name=filename_
            ))

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(gmail_username,gmail_password)
    server.sendmail(mozilla_address, gmail_address, msg.as_string())
    server.close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.exit("Please pass in the name of the pdf to split")

    split(sys.argv[1])
