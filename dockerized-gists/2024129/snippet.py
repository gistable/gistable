import flask


class HelloApp(flask.Flask):
    def __init__(self, import_name):
        super(HelloApp, self).__init__(import_name)
        self.route("/hello")(self.hello)

    def hello(self):
        return "Hello, world!"



class GoodbyeApp(flask.Flask):
    def __init__(self, import_name):
        super(GoodbyeApp, self).__init__(import_name)
        self.route("/goodbye")(self.goodbye)

    def goodbye(self):
        return "Goodbye, world!"


class MyApp(HelloApp, GoodbyeApp):
    def __init__(self, import_name):
        super(MyApp, self).__init__(import_name)
        self.route("/")(self.index)
    
    def index(self):
        return "<a href='{0}'>hello</a> <a href='{1}'>goodbye</a>".format(
            flask.url_for("hello"), flask.url_for("goodbye"))

if __name__ == '__main__':
    MyApp(__name__).run(debug=True)
