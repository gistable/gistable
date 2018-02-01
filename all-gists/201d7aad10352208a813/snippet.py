from ws4py.client.threadedclient import WebSocketClient

class DummyClient(WebSocketClient):
    def opened(self):
        print "Opened websocket"

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        print m

if __name__ == '__main__':
    try:
        ws = DummyClient('wss://www.irccloud.com')
        ws.url = "https://www.irccloud.com" #send the correct Origin header
        ws.extra_headers = [('Cookie','session=XXX’)]
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
