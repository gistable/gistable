# Author = Nikhil Venkat Sonti
# email = nikhilsv92@gmail.com
# github ID = shadowfax92
import sys
from xml.dom.minidom import _get_StringIO
from lxml import html
import requests
import os
import re
import time
import datetime
import csv
import urllib2
from StringIO import StringIO
import multiprocessing as mp
import socket
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import subprocess
import time

new_item_dict = {}

def play_alert():
	# play alert on Mac using say command
    os.system('say "ring ring ring"')

def mail_me(subject, content):
    msg = MIMEMultipart('alternative')
    msgbody = MIMEText(content)
    msg["From"] = "X@gmail.com"
    msg["To"] = "Y@gmail.com"
    msg["Subject"] = subject
    msg.attach(msgbody)
    p = subprocess.Popen(["/usr/sbin/sendmail", "-t"], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out,err) = p.communicate(msg.as_string())
    print 'Mailed = ' + content

def get_content_from_url_and_store():
    try:
        url = 'http://www.flipkart.com/'
        page = requests.get("http://www.flipkart.com/")
        tree = html.parse(StringIO(page.text)).getroot()

        os.system('clear')
        print '\nRUNNING FLIPKART PARSER'

        for i in range(1,8):
            try:
                mail_content = ""
                mail_subject = ""
                name_1 = ""
                name_2 = ""
                print
                xpath_1 = '/html/body/div[1]/div[3]/div/div[9]/div/div[1]/div['+str(i)+']/a/div[4]/text()'
                xpath_2 = '/html/body/div[1]/div[3]/div/div[9]/div/div[1]/div['+str(i)+']/a/div[2]/div/text()'
                xpath_3 = '/html/body/div[1]/div[3]/div/div[9]/div/div[1]/div['+str(i)+']/a/div[1]/text()'
                xpath_4 = '/html/body/div[1]/div[3]/div/div[9]/div/div[1]/div['+str(i)+']/div/div[2]/text()'
                xpath_5_link = '/html/body/div[1]/div[3]/div/div[9]/div/div[1]/div['+str(i)+']/a/div[5]/div[2]/div'

                #sold out check
                try:
                    name_4 = tree.xpath(xpath_4)[0].strip(' \t\n\r')
                    print "sold-out or not = " + name_4
                except Exception, e:
                    pass
                finally:
                    pass

                try:
                    name_1 = tree.xpath(xpath_1)[0].strip(' \t\n\r')
                    print "name-1 = " + name_1
                    if re.search(r'(disk|hard|seagate|external|headphone|headset|phone)', name_1, re.IGNORECASE):
                        play_alert()
                        # mail_subject += name_1 + " "
                    # mail_subject += str(name_1) + " "
                except Exception, e:
                    pass
                finally:
                    pass

                try:
                    name_2 = tree.xpath(xpath_2)[0].strip(' \t\n\r')
                    print "name-2 = " + name_2
                    if re.search(r'(disk|hard|seagate|external|headphone|headset|phone)', name_2, re.IGNORECASE):
                        play_alert()
                        # mail_subject += str(name_2) + " "
                except Exception, e:
                    pass
                finally:
                    pass

                try:
                    name_3 = tree.xpath(xpath_3)[0].strip(' \t\n\r')
                    print "offer percentage/price = " + name_3
                except Exception, e:
                    pass
                finally:
                    pass

                try:
                    name_5 = tree.xpath(xpath_5_link)[0].get('data-url')
                    link = 'http://www.flipkart.com'+name_5
                    print "view/shop link = " + link
                    # print "view/shop link = " + name_5[0].strip(' \t\n\r')
                except Exception, e:
                    pass
                finally:
                    pass

                mail_subject = str(name_1) + " " + str(name_2)
                if mail_subject not in new_item_dict:
                    mail_content += str(name_1) + "\n"
                    mail_content += str(name_2) + "\n"
                    mail_content += str(name_4) + "\n"
                    mail_content += str(name_3) + "\n"
                    mail_content += str(link) + "\n"
                    new_item_dict[mail_subject] = mail_content
                    mail_me(mail_subject, mail_content)
                    play_alert()

            except Exception, e:
                print str(e)
            finally:
                pass
    except Exception, e:
        print 'Something Went Wrong :('
        print 'Exception: ', str(e)
        pass
    finally:
        pass



def main():
    while True:
        get_content_from_url_and_store()
        time.sleep(5)


if __name__ == '__main__':
    main()