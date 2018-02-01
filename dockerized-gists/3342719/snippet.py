import tornado.ioloop
import tornado.web

class Main(tornado.web.RequestHandler):
        def get_current_user(self):
                return self.get_secure_cookie("user")

        @tornado.web.authenticated
        def get(self):
## This work is achieved by decorator @tornado.web.authenticated
                #if not self.current_user:
                #       self.redirect("/login")
                #       return
                username = self.current_user
                self.write('Hi there, '+ username)

class Login(Main):
        def get(self):
                self.render('auth.html')
        def post(self):
                self.set_secure_cookie("user", self.get_argument("username"))
                self.redirect("/")

settings = {
        "cookie_secret":"61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        "login_url":"/login",
        "debug":"True",
        }
application = tornado.web.Application([
        (r"/", Main),
        (r"/login", Login),
        (r"/(style\.css)",tornado.web.StaticFileHandler, {"path": "./css/"}),
        ], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
