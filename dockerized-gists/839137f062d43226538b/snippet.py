#!/usr/bin/env python
class YottaPubSub(object):
    def __init__(_):    _.sessions, _.channels = {}, {}
    def add(_,sid,fun): _.sessions[sid] = fun ; _.sub( sid, [] )
    def pop(_,sid):     _.sessions.pop( sid ) ; _.channels.pop( sid )
    def sub(_,sid,channels): _.channels[sid] = ["*",sid] + channels
    def pub(_,sid,channel,msg):
        for key,func in _.sessions.iteritems():
            if key!=sid  and  channel in _.channels[key]:
                func( sid, channel, msg )
    def app(self, env, start_response):
        import json
        wsock = env['wsgi.websocket']
        sid = str( id( wsock ) )
        send = lambda sid, ch, msg: wsock.send( json.dumps( [2,sid,msg] ) )
        self.add( sid, send )
        try:
            wsock.send( json.dumps( [0, ":HELLO:", {"channels": [sid, "*"]}] ) )
            while 1:
                try:
                    msg = json.loads( wsock.receive() )
                except:
                    break
                if   msg[0]==0: self.sub( sid, msg[2].get('channels', [] ) )
                elif msg[0]==1: self.pub( sid, msg[1], msg )
                else: raise Exception( "ERROR", repr(msg ))
        finally:
            self.pop( sid )
if __name__=='__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler
    WSGIServer( ("", 9028), YottaPubSub().app,
                     handler_class=WebSocketHandler ).serve_forever()
