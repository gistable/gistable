

# idea original from http://codeblog.dhananjaynene.com/2010/01/implementing-request-interceptors-for-tornado/

#fixed bugs

import base64
import logging
import logging.config
import tornado.httpserver
import tornado.ioloop
import tornado.web

log = logging.getLogger("root")

def authenticator(realm,handle,password):
    """
    This method is a sample authenticator.
    It treats authentication as successful
    if the handle and passwords are the same.
    It returns a tuple of handle and user name
    """
    if handle == password :
        return (handle,'User Name')
    return None

def user_extractor(user_data):
    """
    This method extracts the user handle from
    the data structure returned by the authenticator
    """
    return user_data[0]

def basic_authenticate(realm, authenticator,user_extractor) :
    """
    This is a basic authentication interceptor which
    protects the desired URIs and requires
    authentication as per configuration
    """
    def wrapper(self, transforms, *args, **kwargs):

        request = self.request
        format = ''
        clazz = self.__class__
        print 'intercepting for class : %s', clazz
        try:
            auth_hdr = request.headers.get('Authorization')
           
            if auth_hdr == None:
                return False
            if not auth_hdr.startswith('Basic '):
                return False
           
            auth_decoded = base64.decodestring(auth_hdr[6:])
            username, password = auth_decoded.split(':', 2)
           
            user_info = authenticator(realm, unicode(username), password)
            if user_info :
                self._user_info = user_info
                self._current_user = user_extractor(user_info)
                print  'authenticated user is : %s', str(self._user_info)
            else:
                return False
        except Exception, e:
            return False
        return True
    return wrapper

def interceptor(func):
    """
    This is a class decorator which is helpful in configuring
    one or more interceptors which are able to intercept, inspect,
    process and approve or reject further processing of the request
    """
    def classwrapper(cls):
        def wrapper(old):
            def inner(self, transforms, *args, **kwargs):
                print 'Invoking wrapper %s',func
                ret = func(self,transforms,*args,**kwargs)
                if ret :
                    return old(self,transforms,*args,**kwargs)
                else :
                    self._transforms = transforms
                    return self._unauthorized()
            return inner
        cls._execute = wrapper(cls._execute)
        return cls
    return classwrapper

realm = "dummy_realm"

@interceptor(basic_authenticate(realm, authenticator, user_extractor))
class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("Hello, world")

    def _unauthorized(self):
        global realm
        self.set_status(401)
        self.set_header('WWW-Authenticate','Basic realm="%s"' % realm)
        self.write("unauthorized")
        self.finish()


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(7777)
    tornado.ioloop.IOLoop.instance().start()