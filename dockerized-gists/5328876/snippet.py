# by fcicq <fcicq@fcicq.net>, 2013.4.7, GPLv2
# Tornado 3.0 is required.
from tornado.websocket import websocket_connect, WebSocketClientConnection
from tornado.ioloop import IOLoop
from datetime import timedelta

#echo_uri = 'ws://echo.websocket.org'
echo_uri = 'ws://ws.blockchain.info/inv'
PING_TIMEOUT = 15
class myws():
  conn = None
  keepalive = None
  def __init__(self, uri):
    self.uri = uri
    self.doconn()
  def doconn(self):
    w = websocket_connect(self.uri)
    w.add_done_callback(self.wsconnection_cb)
  def dokeepalive(self):
    stream = self.conn.protocol.stream
    if not stream.closed():
      self.keepalive = stream.io_loop.add_timeout(timedelta(seconds=PING_TIMEOUT), self.dokeepalive)
      self.conn.protocol.write_ping("")
    else:
      self.keepalive = None # should never happen
  def wsconnection_cb(self, conn):
    self.conn = conn.result()
    self.conn.on_message = self.message
    self.conn.write_message('{"op":"ping_block"}')
    self.conn.write_message('{"op":"blocks_sub"}')
#    self.conn.write_message('{"op":"unconfirmed_sub"}')
    self.keepalive = IOLoop.instance().add_timeout(timedelta(seconds=PING_TIMEOUT), self.dokeepalive)
  def message(self, message):
    if message is not None:
      print('>> %s' % message)
    else:
      self.close()
  def close(self):
    print('conn closed')
    if self.keepalive is not None:
      keepalive = self.keepalive
      self.keepalive = None
      IOLoop.instance().remove_timeout(keepalive)
    self.doconn()

import signal
def main():
  try:
    io_loop = IOLoop.instance()
    signal.signal(signal.SIGTERM, io_loop.stop)
    myws(echo_uri)
    IOLoop.instance().start()
  except KeyboardInterrupt:
    io_loop.stop()

if __name__ == '__main__':
  main()
