#!/usr/bin/python
import sys
import time
import urllib
import smtplib  
import datetime
import traceback
from bs4 import BeautifulSoup
 
def sendemail(exception=false):
       
    fromaddr = 'from@gmail.com'
    toaddrs  = 'to@gmail.com' 

    if exception:
        msg = 'A new job has been posted on My UB Card.' 
        msg = "\r\n".join([
          "From: from@gmail.com",
          "To: to@gmail.com",
          "Subject: Script Exception",
          "",
          "Exception in your script. Check and fix",
          ])
    else:
        msg = 'A new job has been posted on My UB Card.' 
       
        msg = "\r\n".join([
          "From: from@gmail.com",
          "To: to@gmail.com",
          "Subject: Alert!! New Job Posted",
          "",
          "A new job has been posted on My UB Card. Check and apply.",
          ])
       
    # Gmail Credentials
    username = 'username' 
    password = 'password' 
       
    # The actual mail send  
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.ehlo()
    server.starttls()  
    server.login(username,password)  
    server.sendmail(fromaddr, toaddrs, msg)  
    server.quit()  
 
def openAndCheck(current_count):
    try:
        # print "called with ", current_count
        t = urllib.urlopen("http://myubcard.com/jobs/")
        a = t.read()
        soup = BeautifulSoup(a)
        new_count = len(filter(lambda x: x!=u'\n', soup.find_all("table")[2].contents)[1:-1])
        if new_count>current_count:
            #send mail
            print "will send mail"
            sendemail()
        else:
                #do nothing
            print "do nothing"
        return new_count
    except:
        e = traceback.format_exc()
        #probably send a mail saying that it doesn't work
        sendemail(exception=true)
        return -1
 
if __name__=="__main__":
    sys.stdout.flush()
    initial_count = 0
    current_count = openAndCheck(initial_count)
    while True:
        time.sleep(18000)
        # print "Start---", datetime.datetime.now()
        current_count = openAndCheck(current_count)
        # print "End---", datetime.datetime.now()