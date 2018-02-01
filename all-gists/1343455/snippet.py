"""
Run a websocket and HTTP server on port 7000. The web page served over HTTP
connects to the websocket server and waits for database notifications.

After loading the page, connect to your database and run

=# NOTIFY data, 'some text';

which should make 'some text' appear in the textarea.

To shut down the server, run

=# NOTIFY exit;

which will make the process exit.
"""

from txpostgres import txpostgres
import websocket

from twisted.internet import defer, reactor
from twisted.python import log, util
from twisted.web import resource


# customise this
dsn = ""


class MainPage(resource.Resource):

    isLeaf = True

    def render_GET(self, request):
        return r"""
<html>
  <head>
    <title>notify demo</title>
    <script>
      window.onload = function() {
        var wsclass = window.WebSocket || window.MozWebSocket;
        if (!wsclass) {
            alert('your browser does not support WebSockets');
        }
        else {
            var ws = new wsclass('ws://localhost:7000/data');
            ws.onmessage = function(msg) {
                document.getElementById('text').value += msg.data + '\n';
            }
        }
      }
    </script>
  </head>
  <body>
    <input type="button" value="clear"
           onclick="document.getElementById('text').value = ''"></input>
    <br />
    <textarea id="text" cols="80" rows="30"></textarea>
  </body>
</html>
"""


class Observer(object):

    def __init__(self):
        self.finished = defer.Deferred()
        self.handlers = set()

    def __call__(self, notify):
        if notify.channel == 'exit':
            self.finished.callback(None)
        else:
            for handler in set(self.handlers):
                handler.onNotify(notify.payload)

    def addHandler(self, handler):
        self.handlers.add(handler)

    def removeHandler(self, handler):
        self.handlers.remove(handler)


class Handler(websocket.WebSocketHandler):

    def __init__(self, transport, observer):
        websocket.WebSocketHandler.__init__(self, transport)
        util.println('new client')
        self.observer = observer
        self.observer.addHandler(self)

    def onNotify(self, data):
        self.transport.write(data)

    def connectionLost(self, reason):
        util.println('client disconnected')
        self.observer.removeHandler(self)


conn = txpostgres.Connection()
observer = Observer()
conn.addNotifyObserver(observer)

site = websocket.WebSocketSite(MainPage())
site.addHandler('/data', lambda transport: Handler(transport, observer))

d = conn.connect(dsn)
d.addCallback(lambda _: conn.runOperation('listen data'));
d.addCallback(lambda _: conn.runOperation('listen exit'));
d.addCallback(lambda _: reactor.listenTCP(7000, site))
d.addCallback(lambda _: util.println('listening on port 7000'))

d.addCallback(lambda _: observer.finished)

d.addCallback(lambda _: util.println('shutting down'))
d.addCallback(lambda _: reactor.stop())
d.addErrback(log.err)

reactor.run()