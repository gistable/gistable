#!/usr/bin/env python 
# also check https://gist.github.com/fliphess/7836479

import tornado.ioloop
import tornado.web
import base64
import netaddr
import bcrypt

def require_basic_auth(handler_class):
    """ auth decorator see:
        http://kevinsayscode.tumblr.com/post/7362319243/easy-basic-http-authentication-with-tornado
    """
    def wrap_execute(handler_execute):
        def require_basic_auth(handler, kwargs):
            auth_header = handler.request.headers.get('Authorization')
            if auth_header is None or not auth_header.startswith('Basic '):
                handler.set_status(401)
                handler.set_header('WWW-Authenticate', 'Basic realm=Restricted')
                handler._transforms = []
                handler.finish()
                return False
            auth_decoded = base64.decodestring(auth_header[6:])
            kwargs['basicauth_user'], kwargs['basicauth_pass'] = auth_decoded.split(':', 2)
            return True
        def _execute(self, transforms, *args, **kwargs):
            if not require_basic_auth(self, kwargs):
                return False
            return handler_execute(self, transforms, *args, **kwargs)
        return _execute
    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class

def read_passwd_file(passwdfile='./.htpasswd'):
    with open(passwdfile, "r") as fh:
        content = fh.readlines()
    for item in content:
        item.strip()
    passwords = {}
    for line in content:
        if ":" in line: 
            username, password = line.split(":")
            passwords[username] = password
    return passwords

def verify_password(passwords, username, password):
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(12))
    stored_hash = passwords[username].strip("\n")
    if stored_hash == bcrypt.hashpw(password, stored_hash):
        return True
    else:
        return False

@require_basic_auth
class MainHandler(tornado.web.RequestHandler):
    def get(self, basicauth_user, basicauth_pass):
        passwords = read_passwd_file()
        if verify_password(passwords):
            self.write("Hello, authenticated user")


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()






