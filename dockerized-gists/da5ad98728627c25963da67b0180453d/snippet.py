import threading

from flask import Flask, make_response
import itchat

qrSource = ''

def start_flask():
    flaskApp = Flask('itchat')
    @flaskApp.route('/')
    def return_qr():
        if len(qrSource) < 100:
            return qrSource
        else:
            response = make_response(qrSource)
            response.headers['Content-Type'] = 'image/jpeg'
            return response
    flaskApp.run()
flaskThread = threading.Thread(target=start_flask)
flaskThread.setDaemon(True)
flaskThread.start()

def qrCallback(uuid, status, qrcode):
    if status == '0':
        global qrSource
        qrSource = qrcode
    elif status == '200':
        qrSource = 'Logged in!'
    elif status == '201':
        qrSource = 'Confirm'
itchat.auto_login(True, qrCallback=qrCallback)
@itchat.msg_register(itchat.content.TEXT)
def reply_text(msg):
    return msg['Text']

itchat.run()