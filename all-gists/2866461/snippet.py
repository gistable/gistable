from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import sys, os, subprocess, tempfile

class CycriptBot(irc.IRCClient):
    nickname = "cycriptbot"

    def __init__(self):
        self.process = "SpringBoard"

    def sendCommand(self, command):
        (script, path) = tempfile.mkstemp()
        os.write(script, command)
        cycript = subprocess.Popen(['/usr/bin/cycript', '-p', self.process, path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        returncode = cycript.wait()
        os.close(script)
        os.unlink(path)
        return cycript.stdout.read()

    def signedOn(self):
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "I don't respond to PMs"
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        highlight = self.nickname + ":"
        if msg.startswith(highlight):
            if user == self.factory.main:
                msg = msg[len(highlight):]
                msg = self.sendCommand(msg)
                self.msg(channel, msg)
            else:
                msg = user + ": Why should I listen to you?"
                self.msg(channel, msg)

class CycriptBotFactory(protocol.ClientFactory):
    protocol = CycriptBot

    def __init__(self, main, channel):
        self.channel = channel
        self.main = main

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed: " + reason
        reactor.stop()

if __name__ == '__main__':
    factory = CycriptBotFactory("conradev", "theos")
    reactor.connectTCP("irc.saurik.com", 6667, factory)
    reactor.run()