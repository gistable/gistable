from flask import Flask, request
from gevent.event import AsyncResult
from gevent.wsgi import WSGIServer

app = Flask(__name__)

waiters = []

@app.route("/")
def main():
    return """
        <html><body style='font: bold 5em helvetica'>
            <script src='http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js'></script>
            <script src='/focus/init'></script>
        </body></html>"""

@app.route("/focus/init")
def init():
    return """
        (function client() {
          ( function listen(){ $.getScript( "/focus/listen", listen ) })();
          $( window )
            .focus( function(){ $.getScript( "/focus/focused" ) } ).focus();
        })()
    """

@app.route("/focus/listen")
def listen():
    waiter = AsyncResult()
    waiters.append(waiter)
    return "($('body').html('%s'));" % waiter.get()

@app.route("/focus/focused")
def focused():
    user_agent = request.user_agent.browser
    while waiters:
        waiter = waiters.pop()
        waiter.set(user_agent)
    return ''

http_server = WSGIServer(('', 8000), app)
http_server.serve_forever()