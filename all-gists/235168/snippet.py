#!/usr/bin/env python

def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return ["Hello, World!"]

if __name__ == "__main__":
    from gevent.wsgi import WSGIServer
    
    address = "localhost", 8080
    server = WSGIServer(address, application)
    try:
        print "Server running on port %s:%d. Ctrl+C to quit" % address
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
        print "Bye bye"
