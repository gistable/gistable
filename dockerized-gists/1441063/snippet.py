from flask import Flask

app=Flask(__name__)

@app.route('/')
def index():
    return """
<span id="now">loading<span>
<script type="text/javascript">
window.WebSocket=window.WebSocket || window.MozWebSocket || false;
if(!window.WebSocket){
    alert("No WebSocket Support");
}else {
    var ws=new WebSocket("ws://"+location.host+"/now");
    var now_el=document.getElementById("now");
    ws.onmessage=function(e){
        now_el.innerHTML=e.data;
    }
    ws.onclose=function(){
        now_el.innerHTML='closed';
    }
    
}
</script>
"""

import time
import tornado.web
from tornado.websocket import WebSocketHandler
from tornado.ioloop import PeriodicCallback,IOLoop
import tornado.wsgi

class NowHandler(WebSocketHandler):
    clients=set()
    @staticmethod
    def echo_now():
        for client in NowHandler.clients:
            client.write_message(time.ctime())
    
    def open(self):
        NowHandler.clients.add(self)
    
    def on_close(self):
        NowHandler.clients.remove(self)
        

wsgi_app=tornado.wsgi.WSGIContainer(app)

application=tornado.web.Application([
    (r'/now',NowHandler),
    (r'.*',tornado.web.FallbackHandler,{'fallback':wsgi_app })
])


PeriodicCallback(NowHandler.echo_now,1000).start()

application.listen(5000)
IOLoop.instance().start()