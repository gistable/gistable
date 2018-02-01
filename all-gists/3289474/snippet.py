import flask
from twilio import twiml

app = flask.Flask(__name__)

@app.route('/mic', methods=['POST'])
def karaoke():
    response = twiml.Response()
    with response.dial() as dial:
        dial.conference("Karaoke Party Room")
    return str(response)