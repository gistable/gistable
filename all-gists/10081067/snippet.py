class StdioProtocol(LineReceiver):

    from os import linesep as delimiter

    def connectionMade(self):
        self.connected = True

    def __init__(self, wire):
        self.chat = wire
        wire.output = self

    def lineReceived(self, line):
        try:
            self.chat.sendMessage(line)
        except NotConnectedError as e:
            self.metaMessage(e)
    def sendMessage(self, line):
        if not self.connected:
            raise NotConnectedError("Not connected")
        self.sendLine(str("<{from}> {message}".format(**line) ))