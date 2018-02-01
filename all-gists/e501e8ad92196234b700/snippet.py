#!/usr/bin/python
import socket
import sys

server = "chat.freenode.net"
channel = "#orain"
nick = "Sasha_IRC_bot"

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Connecting to "+ server +"..."
irc.connect((server, 6667))

irc.send("nick "+ nick +"\r\n")
irc.send("PONG\r\n")
irc.send('USER %s %s %s :%s %s\r\n' % (nick, nick, nick, nick, nick[::-1]))
irc.send("join "+ channel +"\r\n")

while 1:
        text = irc.recv(2048)
        print text
        if "PING" in text:
                irc.send("PONG\r\n")
        if text:
                file = open("irc_log.txt", 'a')
                file.write(text)
                file.close()