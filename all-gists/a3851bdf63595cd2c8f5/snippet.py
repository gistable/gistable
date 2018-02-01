#!/usr/bin/python
#
# Version 1.0
# This script will pass a linux HTML header causing safe connect to ignor the host mac address as safeconnect is not developed for *nix machines
# For educational purposes only. 
# Joubin Jabbari 

import sys
import urllib2  
import random
#Reads OS type and picks random one.
array = ["64","ABC","Asturix","Aurora","BackBox","BackTrack","Baltix","Bharat","BlankOn","Bodhi","Buildix","Caixa","Canaima","Corel","CrunchBang","Distribution","Dreamlinux","EasyPeasy","Edubuntu","Element","Elive","Finnix","Fluxbuntu","Freespire","Gibraltar","Gobuntu","Goobuntu","Guadalinex","HP","Hiweed","Impi","Instant","Joli","Kanotix","Karoshi","Knoppix","Kubuntu","Kuki","Kurumin","LEAF","LOUD","Leeenux","LiMux","Linspire","Linux","LinuxMCE","LinuxTLE","LliureX","Lubuntu","MAX","MEPIS","Maemo","MintPPC","Molinux","Moon","Mythbuntu","Neopwn","NepaLinux","Netrunner","Nova","OpenGEU","OpenZaurus","PC/OS","PSUbuntu","Parsix","Peppermint","Pinguy","Poseidon","Progeny","PureOS","Qimo","Rxart","Sabily","Sacix","Skolelinux","SolusOS","Spri","Sunwah","Super","Symphony","TAILS","Trisquel","TurnKey","UberStudent","Ubuntu","Ulteo","Univention","UserLinux","Vinux","Vyatta","Webconverger","XBMC","Xandros","Xubuntu","Ylmf","Zentyal","ZevenOS","Zorin","[edit]","aptosid","dyne:bolic","gNewSense","gOS","gnuLinEx","grml","nUbuntu","puredyne"]
mySystem = random.choice(array)


#opens URL
opener = urllib2.build_opener()

opener.addheaders = [('User-agent', 'Mozilla/5.0 (x11; U; '+mySystem+'; en-US; rv:1.9.1.16) Gecko/20101130 Firefox/3.5.16')]

opener.open('http://'+sys.argv[1]+'')


