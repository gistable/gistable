from contextlib import contextmanager
from django.contrib.messages.storage.base import BaseStorage, Message
from django.test.client import RequestFactory
from django.utils.decorators import method_decorator

class TestMessagesBackend(BaseStorage):
    def __init__(self, request, *args, **kwargs):
        self._loaded_data = []
        super(TestMessagesBackend, self).__init__(request, *args, **kwargs)
        
    def add(self, level, message, extra_tags=''):
        self._loaded_data.append(Message(level, message, extra_tags=extra_tags))


class Messages(object):
    """
    Mixin class for unittest(2).TestCase classes.

    Usage:
        
        class MyTestCase(unittest2.TestCase, Messages):
            def test_my_message_thing(self):
                with self.messages_request() as request:
                    do_something(request)
                    self.assertMessageCount(request, 1)
                    self.assertMessageInRequest(request, "My Message")
                    self.assertMessageNotInRequest(request, "Not My Message")
    """
    def _prepare_request(self, request):
        request._messages = TestMessagesBackend(request)
        
    @method_decorator(contextmanager)
    def messages_request(self):
        request = RequestFactory().get('/')
        self._prepare_request(request)
        yield request
    
    def assertMessageCount(self, request, expected):
        actual_num = len(request._messages)
        if actual_num != expected:
            self.fail('Message count was %d, expected %d' %
                (actual_num, expected))
    
    def assertMessageInRequest(self, request, message, level=None):
        found = [msg for msg in request._messages if msg.message == message]
        if level:
            found = [msg for msg in found if msg.level == level]
        if not found:
            messages = ['%s (%s)' % (msg.message, msg.level) for msg in request._messages]
            if level:
                self.fail("Message %r with level %r not found in request. Available messages: %r" % (message, level, messages))
            else:
                self.fail("Message %r not found in request. Available messages: %r" % (message, messages))
    
    def assertMessageNotInRequest(self, request, message, level=None):
        found = [msg for msg in request._messages if msg.message == message]
        if level:
            found = [msg for msg in found if msg.level == level]
        if found:
            if level:
                self.fail("Message %r with level %r found in request" % (message, level))
            else:
                self.fail("Message %r found in request" % message)