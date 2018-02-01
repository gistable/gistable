# originally from https://github.com/martinrusev/django-redis-sessions
# but use json, not pickle
import json
import pickle
import time
from redis import Redis
from django.utils.encoding import force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.conf import settings


class SessionStore(SessionBase):
    """
    Implements Redis database session store.
    """

    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        self.db = Redis(
            host=getattr(settings, 'SESSION_REDIS_HOST', 'localhost'),
            port=getattr(settings, 'SESSION_REDIS_PORT', 6379),
            db=getattr(settings, 'SESSION_REDIS_DB', 0),
            password=getattr(settings, 'SESSION_REDIS_PASSWORD', None)
        )

    def encode(self, session_dict):
        d = {}
        for k in session_dict:
            # hold openid's hand
            if k.startswith('_yadis') or k.startswith('_openid'):
                d[k] = pickle.dumps(session_dict[k])
            else:
                d[k] = session_dict[k]
        return json.dumps(d)

    def decode(self, session_data):
        # This mirrors SessionBase.decode()'s convention of catching all errors
        try:
            d = json.loads(session_data)
            for k in d:
                # hold openid's hand again
                if k.startswith('_yadis') or k.startswith('_openid'):
                    d[k] = pickle.loads(d[k])
            return d
        except:
            return {}

    def load(self):
        try:
            data = self.db.get(self.session_key)
            return self.decode(data)
        except:
            self.create()
            return {}

    def exists(self, session_key):
        if self.db.exists(session_key):
            return True
        return False


    def create(self):
        while True:
            self.session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if must_create and self.exists(self.session_key):
            raise CreateError
        data = self.encode(self._get_session(no_load=must_create))
        self.db.set(self.session_key, data)
        self.db.expire(self.session_key, self.get_expiry_age())
        # or should this rather be get_expiry_date()?

    def delete(self, session_key=None):
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key
        try:
            self.db.delete(session_key)
        except:
            pass
