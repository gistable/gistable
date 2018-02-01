"Serve a Flask app on a sub-url during localhost development."

from flask import Flask


APPLICATION_ROOT = '/spam'


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return 'Hello, world!'


if __name__ == '__main__':
    # Relevant documents:
    # http://werkzeug.pocoo.org/docs/middlewares/
    # http://flask.pocoo.org/docs/patterns/appdispatch/
    from werkzeug.serving import run_simple
    from werkzeug.wsgi import DispatcherMiddleware
    app.config['DEBUG'] = True
    # Load a dummy app at the root URL to give 404 errors.
    # Serve app at APPLICATION_ROOT for localhost development.
    application = DispatcherMiddleware(Flask('dummy_app'), {
        app.config['APPLICATION_ROOT']: app,
    })
    run_simple('localhost', 5000, application, use_reloader=True)
