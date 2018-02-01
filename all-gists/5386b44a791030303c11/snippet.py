import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import check_output
import datetime

#Globals
emailUsr = "" #sender email user name
emailAddr = "" #sender email address
emailPwd = "" #sender email password
emailRcpt = "" #recipient email address
IP = ""
time = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") 

def main():
    print("The time is: " + time)
    scrapeIfConfig()
    print("IP:" + getIP())
    emailDoc()
    print("Done!")

def setIP(ipstring):
    global IP
    IP = ipstring

def getIP():
    global IP
    return IP

def scrapeIfConfig():
    trimmedIP = check_output(["ifconfig"])[78:92].decode("utf-8")
    setIP(trimmedIP)

def emailDoc():
    #Creating the email.
    msg = MIMEMultipart()
    msg['From'] = emailAddr
    msg['To'] = emailRcpt
    msg['Subject'] = "IP at: " + time 
    body = getIP()
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    #Sending the email.
    server = smtplib.SMTP("smtp.gmail.com", 25) #This is the SMTP server for gmail, it's different for other providers.
    server.ehlo()
    server.starttls()
    print("Logging in as user: " + emailUsr)
    server.login(emailUsr, emailPwd)
    print("Logged in!")  #If it fails to log in, the program will crash and you won't see this.
    print("Sending to address: " + emailRcpt)
    server.sendmail(emailAddr, emailRcpt, text)


main()