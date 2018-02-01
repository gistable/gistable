from flask import Flask
from flask import request
import requests
import subprocess
import json
import time

payload_url = 'https://url-que-notificaremos-quando-o-deploy-terminar/'
app = Flask(__name__)

@app.route("/deploy", methods=['POST'])
def index():
    execute_script("deploy-exemplo-em-powershell")
    notify("deploy realizado")
    return ""

def notify(message):
    payload = {'text' : message}
    r = requests.post(payload_url, data=json.dumps(payload))

def execute_script(script):
    cmd = ["powershell","-ExecutionPolicy", "Bypass", "C:\\deploy\\{0}.ps1".format(script)]

    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out,err = p.communicate()

    if(err):
        raise Exception('Error: ' + str(err))

    return out

if __name__ == "__main__":
    app.run(port=7500, host='0.0.0.0', debug=True, threaded=True)