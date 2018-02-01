import smtplib

gmail_account = 'darkrho@gmail.com'
gmail_pass = 'misuperpass'
to_emails = ['darkrho@gmail.com']

message = """From: %s
To: %s
Subject: python rulz!

Hola :P
""" % (gmail_account, ', '.join(to_emails))

server = smtplib.SMTP('smtp.gmail.com', 587)
server.set_debuglevel(1)
server.ehlo()
server.starttls()
server.login(gmail_account, gmail_pass)
server.sendmail(gmail_account, to_emails, message)
server.quit()


