from tornado import gen
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient

stream = None

def out(data):
    print(data)
    stream.read_until(b"\n", callback=out)

@gen.coroutine
def setup():
    global stream
    stream = yield TCPClient().connect("localhost", 8000)
    stream.read_until(b"\n", callback=out)
    # or could call out() with empty data, to save duplication

if __name__ == '__main__':
    setup()
    IOLoop.current().start()