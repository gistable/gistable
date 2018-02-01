from os import urandom

def random_id():
    """Returns a 20-character random identifier."""
    return urandom(15).encode("base64")[:-1]

def parse_cookie(environ):
    """Returns the cookie from the given WSGI environ as dict."""
    s = environ.get('HTTP_COOKIE', '')
    return dict(map(str.strip, elt.split("=")) for elt in s.split(";")) if s else {}

def dump_cookie(sid, max_age=21600):
    """Returns a cookie header for the given session id."""
    return "sessionid=%s;Max-Age=%s;Path=/;Version=1" % (sid, max_age)

class SessionMiddleware(object):
    class Session(object):
        def __init__(self, store, sid):
            self.store, self.sid, self.data = store, sid, {}
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def destroy(self):
            del self.store.sessions[self.sid]
    
    def __init__(self, app):
        self.app, self.sessions = app, {}
    
    def get_session(self, sid): # TODO make threadsafe
        try:
            return self.sessions[sid]
        except KeyError:
            sid = random_id()
            while sid in self.sessions:
                sid = random_id()
            self.sessions[sid] = session = self.Session(self, sid)
            return session
    
    def __call__(self, environ, start_response):
        session = self.get_session(parse_cookie(environ).get('sessionid'))
        environ['web.session'] = session
        def middleware_start_response(status, headers):
            return start_response(status, headers + [('Set-Cookie', dump_cookie(session.sid))])
        return self.app(environ, middleware_start_response)
