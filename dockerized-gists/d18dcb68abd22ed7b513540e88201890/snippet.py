from flask import Flask, g, request
from flask import render_template, redirect
app = Flask(__name__)


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        callback(response)
    return response


@app.before_request
def before():
    if request.path == "/match":
        @after_this_request
        def after(response):
            print("FOUND")


@app.route('/')
def empty():
    return "EMPTY"


@app.route('/match')
def hello_test():
    return "test"


if __name__ == '__main__':
    app.run(
        debug=True,
        host="0.0.0.0",
        port=7100
    )
