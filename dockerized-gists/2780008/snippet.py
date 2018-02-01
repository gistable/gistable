import os
import smtplib
import argparse
import re
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate, COMMASPACE
from email import Encoders

config = {
    'smtps':[
        'smtp.gmail.com',
        'smtp.qq.com',
        'smtp.sina.com',
        'smtp.sohu.com',
        'smtp.163.com'
            ],
    }

email_content = 'Hello world'
email_subject = 'Hi'

def get_smtp_addr_by_email(email):
    domain = email[email.find('@')+1:]
    for x in config['smtps']:
        if domain in x:
            print x
            return x
    return None

def is_email(email):
    return re.match('^[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+$',email)

def send_email(from_addr, password, to_addrs, cc_addrs, subject, content, attachment_paths, is_debug, html_filename, dctype='application/octet-stream'):
    if is_email(from_addr) is None:
        print 'The address email for from is not a email address'
        return
    #filter those not email address
    to_addrs_list = [x for x in to_addrs if is_email(x)]
    cc_addrs_list = [x for x in cc_addrs if is_email(x)]
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = COMMASPACE.join(to_addrs_list) 
    msg['Date'] = formatdate(localtime = True)
    msg['Cc'] = COMMASPACE.join(cc_addrs_list)
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)
    msgAlternative.attach(MIMEText(content, 'plain'))
    if html_filename:
        try:
            with open(html_filename, 'rb') as htmlfile:
                msgAlternative.attach(MIMEText(htmlfile.read(), 'html'))
        except IOError:
            print "error: Can't open the html file"

    for file_path in attachment_paths:
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            ctype = dctype
        maintype, subtype = ctype.split('/', 1)
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase(maintype, subtype)
                part.set_payload(f.read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                print os.path.basename(file_path)
                msg.attach(part)
        except IOError:
             print "error: Can't open the file %s"%file_path

    try:
        smtp = smtplib.SMTP()
        if is_debug:
            smtp.set_debuglevel(1)
        smtp.connect(get_smtp_addr_by_email(from_addr))
        smtp.login(from_addr, password)
        smtp.sendmail(from_addr, to_addrs_list, msg.as_string())
        smtp.close()
    except smtplib.SMTPAuthenticationError:
        print 'error: SMTPAUthenticationError'
    except smtplib.SMTPServerDisconnected:
        print 'error: The server unexpectedly disconnects'
    except smtplib.SMTPSenderRefused:
        print 'error: Sender address refused'
    except smtplib.SMTPRecipientsRefused:
        print 'error: All recipient addresses refused'
    except smtplib.SMTPDataError:
        print 'error: The SMTP server refused to accept the message data'
    except smtplib.SMTPConnectError:
        print 'error: Error occurred during establishment of a connection with the server'
    except smtplib.SMTPHeloError:
        print 'error: The server refused our "HELO" message'
    
def main():
    parser = argparse.ArgumentParser(description='Send mail with attackment')
    parser.add_argument('-f', '--from_email', default=None, type=str, required=True, help="the sender's email address")
    parser.add_argument('-p', '--password', default=None, type=str, required=True, help="the sender's password")
    parser.add_argument('-t', '--to_emails', default=[], nargs='+', type=str, required=True, help="the reciever's email address")
    parser.add_argument('-c', '--cc_emails', default=[], nargs='+', type=str, help="the Cc email address")
    parser.add_argument('-a', '--attachments', default=[], nargs='+', type=str, help="the attachments file")
    parser.add_argument('-d', '--debug', default=False, type=bool, help="Do you want debug log")
    parser.add_argument('-s', '--subject', default=email_subject, type=str, help="the email's subject")
    parser.add_argument('-r', '--htmlfile', default=None, type=str, help="to send this html file 'often is myself resume'")
    args = parser.parse_args()
    send_email(args.from_email, args.password, args.to_emails, args.cc_emails,
                    args.subject, email_content, args.attachments, args.debug, args.htmlfile)
    parser.parse_args()

if __name__ == '__main__':
    main()