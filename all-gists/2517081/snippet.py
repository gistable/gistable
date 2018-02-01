from smtplib import SMTP
import datetime

debuglevel = 1

smtp = SMTP()
smtp.set_debuglevel(debuglevel)
smtp.connect("smtp.cse.iitb.ac.in",25)
smtp.starttls()
smtp.login('USERNAME HERE', 'PASSWORD HERE')

for line in open("batch.txt").readlines():
    parts = line.split(',')
    from_addr = "FROM" #Example : "Anil Shanbhag <anil@cse.iitb.ac.in>"
    to_addr = "TO"

    subj = "SUBJECT HERE"
    date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )

    message_text = "MESSAGE HERE"

    msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( from_addr, to_addr, subj, date, message_text )

    smtp.sendmail(from_addr, to_addr, msg)

smtp.quit()