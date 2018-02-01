# coding=utf-8
from StringIO import StringIO
from datetime import timedelta

from rx import Observer
from rx.concurrency import TwistedScheduler
from rx.disposables import Disposable
from rx.subjects import Subject
from twisted.internet.protocol import Factory, Protocol, connectionDone
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

scheduler=TwistedScheduler(reactor)  # using this to schedule timeouts

KEEP_ALIVE_TIMEOUT=10  # seconds
READ_TIMEOUT=5  # seconds


class HttpConnection(Protocol):  # Protocol for Twisted
  listener=Subject()  # shared by all connections

  def connectionMade(self):
    self.data_in=Subject()
    self.listener.on_next(self)

  def connectionLost(self, reason=connectionDone):
    self.data_in.on_completed()

  def dataReceived(self, data):
    self.data_in.on_next(data)


class HttpParser(Observer):
  def __init__(self, conn):
    super(HttpParser, self).__init__()
    self.conn=conn
    self.buf=StringIO()
    self.requests_in=Subject()
    self.responses_out=HttpWriter(conn)
    self.keep_alive_timeout_dispose=Disposable.empty()
    self.read_timeout_dispose=Disposable.empty()
    self.keep_alive_timer_on()

  def schedule_timeout(self, seconds):
    def action(scheduler, state=None):
      print 'timeout', seconds
      self.requests_in.on_error(HttpResponse(408, 'Request Timeout'))

    return scheduler.schedule_relative(timedelta(seconds=seconds), action)

  def clear_timeout(self, disposable):
    try:
      disposable.dispose()
    except: # Twisted sometimes complains when we try to cancel timeout after it has already fired
      pass

  def keep_alive_timer_on(self):
    self.keep_alive_timer_off()
    self.keep_alive_timeout_dispose=self.schedule_timeout(KEEP_ALIVE_TIMEOUT)

  def keep_alive_timer_off(self):
    self.clear_timeout(self.keep_alive_timeout_dispose)

  def read_timer_on(self):
    self.read_timer_off()
    self.read_timeout_dispose=self.schedule_timeout(READ_TIMEOUT)

  def read_timer_off(self):
    self.clear_timeout(self.read_timeout_dispose)

  def parse_request(self, buf):
    lines=buf.split('\r\n')
    first_line=lines[0].split()
    if len(first_line)==3:
      self.requests_in.on_next(HttpRequest(self.conn, first_line[0], first_line[1]))
    else:
      self.requests_in.on_error(HttpResponse(400, 'Bad Request'))

  def on_next(self, data):
    self.keep_alive_timer_off()
    self.read_timer_on()
    self.buf.write(data)  # append new data
    buf=self.buf.getvalue()
    eor=buf.find('\r\n\r\n')  # check we've got full request
    if eor>=0:
      self.buf=StringIO()
      self.buf.write(buf[eor+4:])  # leave remainder in buf
      self.parse_request(buf[:eor])
      self.read_timer_off()
      self.keep_alive_timer_on()

  def on_error(self, e):
    print 'parser got error', e
    self.keep_alive_timer_off()
    self.read_timer_off()
    self.requests_in.on_error(HttpResponse(500, 'Internal Server Error'))

  def on_completed(self):
    print 'parser completed'
    self.keep_alive_timer_off()
    self.read_timer_off()
    self.requests_in.on_completed()


class HttpWriter(Observer):
  def __init__(self, conn):
    super(HttpWriter, self).__init__()
    self.conn=conn

  def on_next(self, resp):
    self.conn.transport.write(resp.render())

  def on_error(self, e):
    print 'writer got error', e
    if isinstance(e, HttpResponse):
      self.conn.transport.write(e.render())
    self.conn.transport.loseConnection()

  def on_completed(self):
    print 'writer completed'
    self.conn.transport.loseConnection()


class HttpRequest(object):
  def __init__(self, conn, method, uri):
    self.conn=conn
    self.method=method.upper()
    self.uri=uri

  def __str__(self):
    return '<RxRequest: %s %s>'%(self.method, self.uri)


class HttpResponse(object):
  def __init__(self, status_code, status_text, content=None, headers=None):
    self.status_code=status_code
    self.status_text=status_text
    self.content=content or ''
    self.headers=headers or ('Content-Type: text/plain; charset=utf-8',
                             'Content-Length: '+str(len(self.content)))

  def render(self):
    return 'HTTP/1.1 '+str(self.status_code)+' '+self.status_text+'\r\n'+'\r\n'.join(
      self.headers)+'\r\n\r\n'+self.content

  def __str__(self):
    return '<RxResponse: %d %s>'%(self.status_code, self.status_text)


def accept_connection(conn):
  # wire the data flow
  http=HttpParser(conn)
  conn.data_in.subscribe(http)
  http.requests_in.map(handle_request).subscribe(http.responses_out)


def handle_request(req):
  # print 'req', req.method, req.uri
  return HttpResponse(200, 'OK', content='Hello, '+req.uri+'!')


HttpConnection.listener.subscribe(accept_connection)

# run Twisted
# listening on port 8007
TCP4ServerEndpoint(reactor, 8007).listen(Factory.forProtocol(HttpConnection))
reactor.run()
