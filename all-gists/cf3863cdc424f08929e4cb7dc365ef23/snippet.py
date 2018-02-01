# The SMTP server runs in a separate thread and stores sent messages in a list
#
# Usage:
#
# def test_fn(smtpd):
#    host = smtpd.host
#    port = smtpd.port
#
#    # Run code that send email using an smtp server at host:port
#
#    # Assert that correct messages were received
#    assert len(smtpd.messages) == 5
#    last_message = smtpd.messages[-1]
#    assert last_message.recipients == ['john.doe@example.com']
#

from collections import namedtuple
from smtpd import SMTPServer
from threading import Lock, Thread
import asyncore
import time

import pytest


RecordedMessage = namedtuple(
    'RecordedMessage',
    'peer envelope_from envelope_recipients data',
)


class ThreadSafeList:
    def __init__(self, *args, **kwds):
        self._items = []
        self._lock = Lock()

    def add(self, item):
        with self._lock:
            self._items.append(item)

    def copy(self):
        with self._lock:
            return self._items[:]


class SMTPServerThread(Thread):
    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        self.host_port = None

    def run(self):
        _messages = self.messages

        class _SMTPServer(SMTPServer):
            def process_message(self, peer, mailfrom, rcpttos, data):
                msg = RecordedMessage(peer, mailfrom, rcpttos, data)
                _messages.add(msg)

        self.smtp = _SMTPServer(('127.0.0.1', 0), None)
        self.host_port = self.smtp.getsockname()
        asyncore.loop(timeout=0.1)

    def close(self):
        self.smtp.close()


class SMTPServerFixture:
    def __init__(self):
        self._messages = ThreadSafeList()
        self._thread = SMTPServerThread(self._messages)
        self._thread.start()

    @property
    def host_port(self):
        '''SMTP server's listening address as a (host, port) tuple'''
        while self._thread.host_port is None:
            time.sleep(0.1)
        return self._thread.host_port

    @property
    def host(self):
        return self.host_port[0]

    @property
    def port(self):
        return self.host_port[1]

    @property
    def messages(self):
        '''A list of RecordedMessage objects'''
        return self._messages.copy()

    def close(self):
        self._thread.close()
        self._thread.join(10)
        if self._thread.is_alive():
            raise RuntimeError('smtp server thread did not stop in 10 sec')


@pytest.fixture
def smtpd(request):
    fixture = SMTPServerFixture()
    request.addfinalizer(fixture.close)
    return fixture
