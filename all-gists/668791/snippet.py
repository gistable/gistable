import simplejson

from django.contrib.sessions.backends.base import SessionBase, CreateError

from django_ext.redis_helper import get_redis


class SessionStore(SessionBase):
    """
    A Redis-based session store.
    """
    
    def __init__(self, session_key=None):
        self._redis = get_redis()
        super(SessionStore, self).__init__(session_key)
    
    def load(self):
        session_data = self._redis.get('session:' + self.session_key)
        if session_data is not None:
            return simplejson.loads(session_data)
        self.create()
        return {}
    
    def create(self):
        for i in xrange(10000):
            self.session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return
        raise RuntimeError("Unable to create a new session key.")
    
    def save(self, must_create=False):
        if must_create:
            func = self._redis.setnx
        else:
            func = self._redis.set
        key = 'session:' + self.session_key
        data = simplejson.dumps(self._get_session(no_load=must_create))
        result = func(key, data)
        if must_create and not result:
            raise CreateError
        self._redis.expire(key, self.get_expiry_age())
    
    def exists(self, session_key):
        if self._redis.exists('session:' + session_key):
            return True
        return False
    
    def delete(self, session_key=None):
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key
        self._redis.delete('session:' + session_key)