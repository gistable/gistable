# Python
import time

class CallbackModule(object):
    '''
    Delay after Rackspace DNS API requests to avoid rate limit (20/minute).
    '''

    def _rate_limit(self):
        role_name = getattr(getattr(self, 'task', None), 'role_name', '')
        if role_name == 'rax-dns':
            time.sleep(4) # need to wait a little longer for some reason.

    def runner_on_ok(self, host, res):
        self._rate_limit()

    def runner_on_error(self, host, res):
        self._rate_limit()
