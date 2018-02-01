#!/usr/bin/env python

from socket import *

def flames(input_name1, input_name2):

        input_name1 = input_name1.lower().strip().split()
        input_name2 = input_name2.lower().strip().split()

        name1=[]
        for i in range( len(input_name1) ):
            name1 = name1 + list( input_name1[i] )
        name2=[]
        for i in range( len(input_name2) ):
            name2 = name2 + list( input_name2[i] )

        if name1 != name2:
            delete_name1_char=0
            for walk in range( len(name1) ):
                if name1[walk] in name2:
                    name2.remove( name1[walk] )
                    delete_name1_char+=1

            count = len(name1)+len(name2)-delete_name1_char
            flames = list( "Friends Lover Affection Marriage Enemy Sister".split() )

            flames_count=0
            while ( len(flames)!=1 ):
                for i in range(count):
                    if i == max ( range(count) ):
                        flames.remove( flames[flames_count] )
                        flames_count-=1
                    flames_count += 1
                    if flames_count > len(flames)-1: flames_count=0

            return flames[0]

        elif name1==name2:
            return "Please enter different names"

        else:
            return "Error!, please enter names correctly"

def command(cmd):
    irc.send(cmd)

def JOIN(aChannel):
    cmd = "JOIN %s\r\n" %aChannel
    command(cmd)

def NICK(myNickName):
    cmd = "NICK %s\r\n" %myNickName
    command(cmd)

def USER (UserName, HostName, ServerName, RealName):
    cmd = "USER %s %s %s :%s\r\n" %(UserName, HostName, ServerName, RealName )
    command(cmd)

def PRIVMSG(msg):
    cmd = "PRIVMSG %s\r\n" %msg
    command(cmd)

OnScreen = " welcome to Flames Bot, \n Give it a try."
print OnScreen


HOST = 'irc.freenode.net'
PORT = 6667

NickName = "TheFLAMES"
UserName = "KnolZone"
HostName = "0Host"
ServerName = "0Server"
RealName = "Python27"

irc = socket( AF_INET, SOCK_STREAM )

ADDR = (HOST, PORT)
irc.connect ( ADDR )

NICK(NickName)
USER(UserName, HostName, ServerName, RealName)

channelName = "##getFLAMES"
JOIN(channelName)

while True:

   data = irc.recv ( 4096 )

   if data.find ( 'PING' ) != -1:
      irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )

   elif data.find ( 'PRIVMSG' ) != -1:

      data = data.replace("!", ":").split(":")
      nick = data[1]
      message = data[3]
      destination = data[2].split()[2]

      if message.lower().find("%flames") != -1:

         message = message.replace("%flames","").strip()
         name1, name2 = message.split(";")
         name1.strip()
         name2.strip()

         try:

            ourFlames = flames(name1, name2)
            msg = nick + " :" + nick + ": " + ourFlames
            PRIVMSG(msg)

         except:
                error = "Wrong Input. Check Again!"
                msg = nick + " :" + nick + ": " + error
                PRIVMSG(msg)
                pass
