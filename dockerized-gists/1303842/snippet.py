#!/usr/bin/python

# Equivalent of "tail -f" as a webpage using websocket
# Usage: webtail.py PORT FILENAME
# Tested with tornado 2.1

# Thanks to Thomas Pelletier for it's great introduction to tornado+websocket
# http://thomas.pelletier.im/2010/08/websocket-tornado-redis/

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import sys
import os

PORT = int(sys.argv[1])
FILENAME = sys.argv[2]
LISTENERS = []
TEMPLATE = """
<!DOCTYPE>
<html>
<head>
    <title>WebTail: %s</title>
</head>
<body>
    <div id="file"></div>
    <script type="text/javascript" charset="utf-8">
        function write_line(l) {
            document.getElementById('file').innerHTML += '<p>' + l + '</p>';
        }

        if ("MozWebSocket" in window) {
            WebSocket = MozWebSocket;
        }

        if (WebSocket) {
            var ws = new WebSocket("ws://%s/tail/");
            ws.onopen = function() {};
            ws.onmessage = function (evt) {
                write_line(evt.data);
            };
            ws.onclose = function() {};
        } else {
            alert("WebSocket not supported");
        }
    </script>
</body>
</html>
"""

tailed_file = open(FILENAME)
tailed_file.seek(os.path.getsize(FILENAME))


def check_file():
    where = tailed_file.tell()
    line = tailed_file.readline()
    if not line:
        tailed_file.seek(where)
    else:
        print "File refresh"
        for element in LISTENERS:
            element.write_message(line)


class TailHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "WebSocket open"
        LISTENERS.append(self)

    def on_message(self, message):
        pass

    def on_close(self):
        print "WebSocket close"
        try:
            LISTENERS.remove(self)
        except:
            pass


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(TEMPLATE % (FILENAME, self.request.host))


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/tail/', TailHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)

    tailed_callback = tornado.ioloop.PeriodicCallback(check_file, 500)
    tailed_callback.start()

    io_loop = tornado.ioloop.IOLoop.instance()
    try:
        io_loop.start()
    except SystemExit, KeyboardInterrupt:
        io_loop.stop()
        tailed_file.close()
