#!/usr/bin/python
# The idea behind this script is if plugging a RaspberryPi into a foreign network whilst running it headless
# (i.e. without a monitor/TV), you need to know what the IP address is to SSH into it.
#
# This script emails you the IP address if it detects an ethernet address other than it's usual address
# that it normally has, i.e. on your home network.  

import smtplib, string, subprocess, time

################################################
###### Remember to set all constants here ######
################################################
FIXED_IP = '10.0.1.2'
IP_FILEPATH = '/home/pi/current_ip.txt'
SMTP_USERNAME = 'feersumendjinn@gmail.com'
SMTP_PASSWORD = 'password'
SMTP_RECIPIENT = 'feersumendjinn@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SSL_PORT = 465
################################################

adapter = 'eth0:'
ipaddr_string = 'ip -4 addr > ' + IP_FILEPATH
subprocess.call(ipaddr_string, shell=True)
inet_string = ''

ip_file = file(IP_FILEPATH, 'r')
for line in ip_file:
        
    if adapter in line:
        inet_line = ip_file.next()
        _time = time.asctime()
        inet_string = inet_line[9:(inet_line.index('/'))]

        if inet_string != FIXED_IP:

            p = subprocess.Popen(["runlevel"], stdout=subprocess.PIPE)
            out, err=p.communicate()
            print out
            print out[2]
            if out[2] == '0':
                print 'Halt detected'
                exit(0)
            if out [2] == '6':
                print 'Shutdown detected'
                exit(0)

            SUBJECT = 'IP Address from Raspberry Pi at: %s' % time.asctime()
            TO = SMTP_RECIPIENT
            FROM = SMTP_USERNAME
            text = 'The IP address is: %s' % inet_string
            BODY = string.join((
                'From: %s' % FROM,
                'To: %s' % TO,
                'Subject: %s' % SUBJECT,
                '',
                text
                ), '\r\n')
            server = smtplib.SMTP_SSL(SMTP_SERVER, SSL_PORT)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM, [TO], BODY)
            server.quit()
            

            
            
            print '[' + '\033[36;1m' + 'info'  + '\033[0m' + ']' + ' Emailing eth0 IP address ' + inet_string + ' to ' + TO + ' from ' + FROM
  
        elif inet_string == FIXED_IP:
            print '[' + '\033[32;1m' + ' ok '  + '\033[0m' + ']' + ' Normal IP address' + inet_string + 'found'

        else:
            print '[' + '\033[31;1m' + 'warning'  + '\033[0m' + ']' + adapter +' not found in file!'


ip_file.close()























