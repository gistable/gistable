
import soaplib
from soaplib.core.service import rpc, soap,  DefinitionBase
from soaplib.core.model.primitive import String, Integer
from soaplib.core.server import wsgi
from soaplib.core.model.clazz import Array
from flask import Flask


flask_app = Flask(__name__)

@flask_app.route("/")
def hello():
    return "Hello World!"


class HelloWorldService(DefinitionBase):
    @rpc(String,Integer,_returns=Array(String))
    def say_hello(self,name,times):
        results = []
        for i in range(0,times):
            results.append('Hello, %s'%name)
        return results


if __name__=='__main__':
    try:
        from werkzeug.wsgi import DispatcherMiddleware

        soap_application = soaplib.core.Application([HelloWorldService], 'tns')
        wsgi_application = wsgi.Application(soap_application)

        flask_app.wsgi_app = DispatcherMiddleware(flask_app.wsgi_app, {
            '/soap':        wsgi_application,
            })

        flask_app.run()
    except ImportError:
        print "Error: example server code requires Python >= 2.5"
