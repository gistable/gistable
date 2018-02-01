# -*- coding: utf-8 -*-
from uuid import uuid4

from datetime import timedelta

from couchbase import Couchbase

from couchbase import FMT_PICKLE

from couchbase.exceptions import NotFoundError

from werkzeug.datastructures import CallbackDict

from flask.sessions import SessionInterface, SessionMixin


class CouchbaseSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class CouchbaseSessionInterface(SessionInterface):
    session_class = CouchbaseSession

    def __init__(self, couch=None, prefix='session:', serializer=FMT_PICKLE):
        if couch is None:
            couch = Couchbase.connect(bucket='sessions', host='localhost')
        self.couch = couch
        self.prefix = prefix
        self.serializer = serializer

    def generate_sid(self):
        return str(uuid4())

    def get_couch_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        try:
            data = self.couch.get(self.prefix + sid)
            return self.session_class(data.value, sid=sid)
        except NotFoundError:
            pass
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            try:
                self.couch.delete(self.prefix + session.sid)
            except NotFoundError:
                pass
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        couch_exp = self.get_couch_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        self.couch.set(self.prefix + session.sid, dict(session),
                        format=self.serializer,
                        ttl=int(couch_exp.total_seconds()))
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)
