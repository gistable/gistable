"""Demonstration of server-sent events with Tornado. To see the
stream, you can either point your browser to ``http://localhost:8080``
or use ``curl`` like so::

  $ curl http://localhost:8080/events

"""

import signal
from tornado import web, gen
from tornado.options import options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.iostream import StreamClosedError

html = """
<div id="messages"></div>
<script type="text/javascript">
  var source = new EventSource('/events');
  source.onmessage = function(message) {
    var div = document.getElementById("messages");
    div.innerHTML = message.data + "<br>" + div.innerHTML;
  };
</script>"""

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

class DataSource(object):
    """Generic object for producing data to feed to clients."""
    def __init__(self, initial_data=None):
        self._data = initial_data
    
    @property
    def data(self):
        return self._data
        
    @data.setter
    def data(self, new_data):
        self._data = new_data

class EventSource(web.RequestHandler):
    """Basic handler for server-sent events."""
    def initialize(self, source):
        """The ``source`` parameter is a string that is updated with
        new data. The :class:`EventSouce` instance will continuously
        check if it is updated and publish to clients when it is.

        """
        self.source = source
        self._last = None
        self.set_header('content-type', 'text/event-stream')
        self.set_header('cache-control', 'no-cache')

    @gen.coroutine
    def publish(self, data):
        """Pushes data to a listener."""
        try:
            self.write('data: {}\n\n'.format(data))
            yield self.flush()
        except StreamClosedError:
            pass

    @gen.coroutine
    def get(self):
        while True:
            if self.source.data != self._last:
                yield self.publish(self.source.data)
                self._last = self.source.data
            else:
                yield gen.sleep(0.005)

class MainHandler(web.RequestHandler):
    def get(self):
        self.write(html)

if __name__ == "__main__":
    options.parse_command_line()

    generator = fibonacci()
    publisher = DataSource(next(generator))
    def get_next():
        publisher.data = next(generator)
        print(publisher.data)
    checker = PeriodicCallback(lambda: get_next(), 1000.)
    checker.start()
    
    app = web.Application(
        [
            (r'/', MainHandler),
            (r'/events', EventSource, dict(source=publisher))
        ],
        debug=True
    )
    server = HTTPServer(app)
    server.listen(8080)
    signal.signal(signal.SIGINT, lambda x, y: IOLoop.instance().stop())
    IOLoop.instance().start()
