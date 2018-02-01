#
# before run $ sudo -E pip install Flask
#
# To run: $ python fake-server-chaos.py
#
#
from flask import Flask, request
import time
from threading import Thread

app = Flask(__name__)

#
# curl http://localhost:8080/ok
#
@app.route('/ok')
def ok():
    return 'OK'

#
# curl http://localhost:8080/echo?msg=test
#
@app.route('/echo',methods=['GET', 'POST'])
def echo():
    return str(request.args['msg'])

#
# curl http://localhost:8080/delay?t=10
# 
@app.route('/delay')
def delay():
    time.sleep(float(request.args.get('t',5)))
    return 'OK'

#
# curl http://localhost:8080/hang
#
@app.route('/hang')
def hang():
    time.sleep(30)
    return 'OK'

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080)
