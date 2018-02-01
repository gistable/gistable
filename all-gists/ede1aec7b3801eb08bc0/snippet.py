from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from twisted.python import log

class BetBot(irc.IRCClient):

    nickname = "INSERT YOUR TWITCH USERNAME"
    password = "oauth: GENERATE YOUR OAUTH TWITCH TOKEN SOMEWHERE"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        print "Signed on"
        self.join(self.factory.channel)

    def joined(self, channel):
        print "Joined " + channel

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]
        print user, msg
        if "Place your bets!" in msg:
            reply = "!bet combo 1%" # This is an example automatic bet - I like to bet only 1% to not get fucked by variance
            self.msg(channel, reply)
            print "Sent '" + reply + "' to " + channel


class CobaltBetFactory(protocol.ClientFactory):

    def __init__(self):
        self.channel = "#bot_cobalt"

    def buildProtocol(self, addr):
        p = BetBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    f = CobaltBetFactory()
    reactor.connectTCP("irc.twitch.tv", 6667, f)
    reactor.run()
