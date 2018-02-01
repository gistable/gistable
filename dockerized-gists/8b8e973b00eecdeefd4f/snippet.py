"""python-mailer.py

Author : Vishnu Ashok
Contact : thisisvishnuashok@gmail.com
          thisisvishnuashok@hotmail.com
GitHub : http://github.com/p53ud0k0d3

    This is a simple email client program, which can be used to send emails from Gmail and Hotmail.
    You must enable "Allow less secure apps" in Gmail settings.
"""
import smtplib
import string

def main():

    print "======"
    print "MAILER"
    print "======\n\n"
    print "1. Gmail\n2. Hotmail\n3. Exit"
    ch = int(raw_input("Select an option : "))
    if ch == 1:
        gmail()
    elif ch == 2:
        hotmail()
    elif ch == 3:
        exit()
    else:
        print "Invalid option"


def gmail():
    print "\n"   
    uid = raw_input("Gmail_id : ")
    pwd = raw_input("Password : ")
    to = raw_input("\nTo : ")
    subject = raw_input("Subject : ")
    content = raw_input("Message : ")
    mail_server = 'smtp.gmail.com'
    message = string.join((
        "From : %s" % uid,
        "To : %s" % to,
        "Subject : %s" % subject,
        "",
        content,
    ), "\r\n")   
    send_mail(uid, pwd, to, message, mail_server)
    
def hotmail():
    print "\n"
    uid = raw_input("Hotmail_id : ")
    pwd = raw_input("Password : ")
    to = raw_input("\nTo : ")
    subject = raw_input("Subject : ")
    content = raw_input("Message : ")
    mail_server = 'smptp.live.com'
    message = string.join((
        "From : %s" % uid,
        "To : %s" % to,
        "Subject : %s" % subject,
        "",
        content,
    ), "\r\n")
    send_mail(uid, pwd, to, message, mail_server)
    
def send_mail(uid, pwd, to, message, mail_server):
    server = smtplib.SMTP(mail_server, 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(uid, pwd)
    server.sendmail(uid, to, message)
    server.close()
    
if __name__ == "__main__":
    main()