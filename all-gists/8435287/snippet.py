"""
This is a simple example of WebSocket + Tornado + Simple EventEmitters usage.
    Thanks to pyee by https://github.com/jesusabdullah
    @Author:: Narayanaperumal G <gnperumal@gmail.com>
"""
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from collections import defaultdict


# This is ugly but I did not want to create multiple files for a so trivial
# example.
TEMPLATE = """
<!DOCTYPE>
<html>
<head>
    <title>WebSocket + Tornado + Simple EventEmitters Demo</title>
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.4.2.min.js"></script>
</head>
<body>
    <h1>Hello world</h1>
    <form method='POST' action='./'>
        <textarea name='data' id="data"></textarea>
        <div><input type='submit'></div>
    </form>
    <div id="log"></div>
    <script type="text/javascript" charset="utf-8">
        $(document).ready(function(){

            $('form').submit(function(event){
                var value = $('#data').val();
                $.post("./", { data: value }, function(data){
                    $("#data").val('');
                });
                return false;
            });


            if ("WebSocket" in window) {
              var ws = new WebSocket("ws://127.0.0.1:8888/realtime/");
              ws.onopen = function() {};
              ws.onmessage = function (evt) {
                  var received_msg = evt.data;
                  var html = $("#log").html();
                  html += "<p>"+received_msg+"</p>";
                  $("#log").html(html);
              };
              ws.onclose = function() {};
            } else {
              alert("WebSocket not supported");
            }
        });
    </script>
</body>
</html>
"""


LISTENERS = []


class EventEmitter(object):
    """The EventEmitter class.

    (Special) Events
    ----------------

    -   'new_listener': Fires whenever a new listener is created. Listeners for this
    event do not fire upon their own creation.

    -   'error': When emitted raises an Exception by default, behavior can be overriden by
    attaching callback to the event.

    For example::

        @ee.on('error')
        def onError(message):
            logging.err(message)

        ee.emit('error', Exception('something blew up'))

    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventEmitter, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the EE.
        """
        self._events = defaultdict(list)

    def on(self, event, f=None):
        """Registers the function ``f`` to the event name ``event``.

        If ``f`` isn't provided, this method returns a function that
        takes ``f`` as a callback; in other words, you can use this method
        as a decorator, like so:

            @ee.on('data')
            def data_handler(data):
                print data

        """

        def _on(f):
            # Fire 'new_listener' *before* adding the new listener!
            self.emit('new_listener', event, f)

            # Add the necessary function
            evts = event.split(" ")
            for evt in evts:
                self._events[evt].append(f)

            # Return original function so removal works
            return f

        if f is None:
            return _on
        else:
            return _on(f)

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` to each attached function. Returns
        ``True`` if any functions are attached to ``event``; otherwise returns
        ``False``.

        Example:

            ee.emit('data', '00101001')

        Assuming ``data`` is an attached function, this will call
        ``data('00101001')'``.

        """
        handled = False

        # Pass the args to each function in the events dict
        for f in self._events[event]:
            f(*args, **kwargs)
            handled = True

        if not handled and event == 'error':
            raise Exception("Uncaught 'error' event.")

        return handled

    def once(self, event, f=None):
        """The same as ``ee.on``, except that the listener is automatically
        removed after being called.
        """
        def _once(f):
            def g(*args, **kwargs):
                f(*args, **kwargs)
                self.remove_listener(event, g)
            return g

        if f is None:
            return lambda f: self.on(event, _once(f))
        else:
            self.on(event, _once(f))

    def remove_listener(self, event, f):
        """Removes the function ``f`` from ``event``.

        Requires that ``f`` is not closed over by ``ee.on``. (In other words,
        it is, unfortunately, not possible to use this with the decorator
        style is.)

        """
        self._events[event].remove(f)

    def remove_all_listeners(self, event=None):
        """Remove all listeners attached to ``event``.
        """
        if event is not None:
            self._events[event] = []
        else:
            self._events = None
            self._events = defaultdict(list)

    def listeners(self, event):
        """Returns the list of all listeners registered to the ``event``.
        """
        return self._events[event]


ee = EventEmitter()


@ee.on('data onopen')
def data_listener(*args, **kwargs):
    if len(args) > 0:
        for element in LISTENERS:
            element.write_message(unicode(args[0]))


class FormHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(TEMPLATE)

    def post(self):
        data = self.request.arguments['data'][0]
        ee.emit('data', data)


class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        LISTENERS.append(self)
        ee.emit("onopen", "Welcome to Realtime communitaction!")

    def on_message(self, message):
        pass

    def on_close(self):
        LISTENERS.remove(self)


settings = {
    'auto_reload': True,
}

application = tornado.web.Application([
    (r'/', FormHandler),
    (r'/realtime/', RealtimeHandler),
], **settings)


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()