import requests
import flask

app = flask.Flask(__name__)


@app.route('/suck')
def suck():
    return requests.get('https://httpbin.org/delay/10')


@app.route('/fuck')
def fuck():
    return 'fuck you'