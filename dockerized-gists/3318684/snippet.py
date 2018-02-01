import os, subprocess, base64
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

define("port",default=8888,type=int)
define("branch",default="master")
define("access",type=str,multiple=True)

class MainHandler(tornado.web.RequestHandler):
    def get(self,path):
        # check user access
        auth_header = self.request.headers.get('Authorization') or ""
        authenticated = not len(options.access)
        if not authenticated and auth_header.startswith('Basic '):
            authenticated = base64.decodestring(auth_header[6:]) in options.access
        if not authenticated:
            self.set_status(401)
            self.set_header('WWW-Authenticate', 'Basic realm=Restricted')
            self._transforms = []
            self.finish()
            return
        # check not escaping chroot
        if os.path.commonprefix([os.path.abspath(path),os.getcwd()]) != os.getcwd():
            raise tornado.web.HTTPError(418)
        # get the file to serve
        try:
            body = subprocess.check_output(["git","show","%s:%s"%(options.branch,path)])
        except subprocess.CalledProcessError:
            raise tornado.web.HTTPError(404)
        # and set its content-type
        self.content_type = subprocess.Popen(["file","-i","-b","-"],stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=subprocess.STDOUT).communicate(input=body)[0]
        # serve it
        self.write(body)
        

application = tornado.web.Application([
    (r"/(.*)", MainHandler),
])

if __name__ == "__main__":
    parse_command_line()
    application.listen(options.port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "bye!"