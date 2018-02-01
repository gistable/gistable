import io
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/logo.jpg')
def logo():
    """Serves the logo image."""

    with open("logo.jpg", 'rb') as bites:
        return send_file(
                     io.BytesIO(bites.read()),
                     attachment_filename='logo.jpeg',
                     mimetype='image/jpg'
               )