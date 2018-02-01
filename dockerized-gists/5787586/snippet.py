# -*- coding: utf-8 -*-
from flask import Flask, send_file
import qrcode
from StringIO import StringIO

app = Flask(__name__)

@app.route("/qr/<path:url>")
@app.route("/qr")
def qr_route(url="http://dongcorp.org"):
    qr = qrcode.make(url)
    img = StringIO()
    qr.save(img)
    img.seek(0)
    return send_file(img, mimetype="image/png")
