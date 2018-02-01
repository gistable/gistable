import flask

class RoutingData(object):
    def __init__(self, args, kwargs):
        super(RoutingData, self).__init__()
        self.args = args
        self.kwargs = kwargs

def route(*args, **kwargs):
    def wrap(fn):
        l = getattr(fn, '_routing_data', [])
        l.append(RoutingData(args, kwargs))
        fn._routing_data = l
        return fn
    return wrap

class SuperFlask(flask.Flask):
    def __init__(self, import_name):
        super(SuperFlask, self).__init__(import_name)
        self.endpoint_prefix = None
        for name in dir(self):
            if hasattr(getattr(self, name), ("_routing_data")):
                fn = getattr(self, name)
                rds = fn._routing_data
                for rd in rds:
                    self.route(*rd.args, **rd.kwargs)(fn)

### Usage ###

class HelloApp(SuperFlask):
    @route("/hello")
    def hello(self):
        return "Hello, world!"

class GoodbyeApp(SuperFlask):
    @route("/goodbye")
    def goodbye(self):
        return "Goodbye, world!"

class MyApp(HelloApp, GoodbyeApp):
    @route("/")
    def index(self):
        return "<a href='{0}'>hello</a> <a href='{1}'>goodbye</a>".format(
            flask.url_for("hello"), flask.url_for("goodbye"))

if __name__ == '__main__':
    MyApp(__name__).run(debug=True)