from flask import Flask, make_response, redirect, session, url_for

SECRET_KEY = 'develop'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    return '<a href="%s">Go here.</a>' % url_for('do_redirect')

@app.route('/redirect/')
def do_redirect():
    session['hello'] = 'world!'
    return redirect(url_for('dump_session'))

@app.route('/session/')
def dump_session():
    response = make_response(repr(session))
    response.content_type = 'text/plain'
    return response

if __name__ == '__main__':
    app.run()
