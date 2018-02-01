import os
import uuid
import marshal
import binascii

import tornado.web


def Session(func):
    def warpper(self, *args, **kwargs):
        self.require_setting("session_path", "Session")
        _SESS_ID = self.get_secure_cookie("_SESS_ID", None)
        if not _SESS_ID:
            _SESS_ID = binascii.b2a_hex(uuid.uuid4().bytes)
            self.set_secure_cookie("_SESS_ID", _SESS_ID)
        sess_file_path = os.path.join(self.settings['session_path'], _SESS_ID + ".ses")

        try:
            sess_file = open(sess_file_path, "r")
        except IOError:
            sess_file = open(sess_file_path, "w")
            sess_file.close()
            self.sessions = {}
        else:
            os.utime(sess_file_path, None)
            sessions = sess_file.read()
            if sessions:
                self.sessions = marshal.loads(sessions)
            else:
                self.sessions = {}
            sess_file.close()

        return_value = func(self, *args, **kwargs)

        sess_file = open(sess_file_path, "w")
        sess_file.write(marshal.dumps(self.sessions))
        sess_file.close()

        return return_value
    return warpper

class TestHandler(tornado.web.RequestHandler):
    @Session
    def get(self):
        print self.sessions