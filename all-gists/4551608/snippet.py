#!/usr/bin/env python2

import socket, ssl, re, hashlib
from datetime import date

# PDF URL on Is-Academia
URL = "/imoniteur_ISAP/!ETURELEVENOTES.pdf?ww_i_inscrblocFiltrage=XXXXXXXXXXXXX&ww_i_unite=10100&ww_i_inscription=XXX"

# GASPAR username
USERNAME = ""

# Gaspar password
PASSWORD = ""

# Email to deliver notification to
EMAIL = "" 

def give_me_a_socket():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    # Wrap into a ssl socket
    s = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_SSLv2)

    s.connect(("isa.epfl.ch", 443))

    return s


def get_from_http_response(s):
    headers = ""
    content = ""

    try :
        # Phase 1 : Get headers

        data = "T"

        while headers.find("\r\n\r\n") == -1 and data != "":
            data = s.recv(1)
            headers += data

        s.settimeout(3) #As server has answered, we dosen't have to wait longer

        # Phase 2: Get content
        content = ""
        data = "T"
        while data != "":
            data = s.recv(1024)
            content += data


    except:

        pass

    return (headers, content)

def alerte():

    import smtplib

    # Import the email modules we'll need
    from email.mime.text import MIMEText

    # Create a text/plain message
    msg = MIMEText("http://isa.epfl.ch" + URL)


    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = "Notes changed on IS-Academia"
    msg['From'] = "noreply@epflmemes.ch"
    msg['To'] = EMAIL

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP_SSL()
    s.connect("mail.epfl.ch")
    s.login(USERNAME, PASSWORD)
    s.sendmail(EMAIL, [EMAIL], msg.as_string())
    s.quit()

# Send HTTP request
s = give_me_a_socket()

s.sendall("POST /imoniteur_ISAP/!logins.tryToConnect HTTP/1.1\r\nHost: isa.epfl.ch\r\nUser-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.2.13) Gecko/20101203 Firefox/3.6\r\n");
s.sendall("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3\r\n")
s.sendall("Accept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7\r\nConnection: closed\r\n")
s.sendall("Content-Type: application/x-www-form-urlencoded\r\n")
s.sendall("Content-Length: " + str(len(USERNAME) + len(PASSWORD) + len("&ww_x_password=ww_x_username=&ww_x_urlAppelant=")) + "\r\n\r\n")
s.sendall("ww_x_username=" + USERNAME + "&ww_x_password=" + PASSWORD + "&ww_x_urlAppelant=")

#s.sendall("GET " + URL + " HTTP/1.0\r\nHost: infowww.epfl.ch\r\n\r\n")


(headers, content) = get_from_http_response(s)


cookie = re.search('\nSet-Cookie: (.*);secure\r', headers)

if cookie and cookie.group(1):

    s = give_me_a_socket()


    s.sendall("GET " + URL + " HTTP/1.0\r\n");
    s.sendall("Cookie: " + cookie.group(1) + "\r\n")
    s.sendall("Host:  isa.epfl.ch\r\n\r\n")

    (headers, content) = get_from_http_response(s)

    currentHash = hashlib.sha224(content).hexdigest()
    try:
        lastHash = open('verinote.hash', 'r').read()
    except IOError:
        lastHash = None

    currentDay = str(date.today().day)

    try:
        lastDay = open('verinote.day', 'r').read()
    except IOError:
        lastDay = None

    if currentHash != lastHash:
        if currentDay == lastDay:
            print "NOTE CHANGE"
            alerte()

        else:
            print "Day changed."
            open('verinote.day', 'w').write(currentDay)

        open('verinote.hash', 'w').write(currentHash)
    else:
        print "Nothing changed"

else:
    print "Hoho, pas de cookie defini. Mauvais mot de passe ?"


