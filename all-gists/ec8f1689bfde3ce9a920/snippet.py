import sys, threading, time
from stem.control import Controller
from stem import SocketError, UnsatisfiableRequest
import stem.process
from stem.util import term
from flask import Flask

import socks

WEB_PORT = 8080
CONTROL_PORT = 7001
SOCKS_PORT = 7000
HIDDEN_SERVICE_DIR = '/tmp/tor/'


app = Flask(__name__)

@app.route('/')
def index():
    return "hello world"

def start_web_app():
    print 'Starting web app'
    app.run(port=WEB_PORT, threaded=True)

def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print(term.format(line, term.Color.BLUE))

def main():
    print(term.format("Starting Tor:\n", term.Attr.BOLD))

    tor_process = stem.process.launch_tor_with_config(
      config = {
        'SocksPort': str(SOCKS_PORT),
        'ControlPort': str(CONTROL_PORT),
        'ExitNodes': '{ru}',
      },
      init_msg_handler = print_bootstrap_lines,
    )

    # Start the flask web app in a separate thread
    t = threading.Thread(target=start_web_app)
    t.daemon = True
    t.start()

    # Connect to the Tor control port
    try:
        c = Controller.from_port(port=CONTROL_PORT)
        c.authenticate()
    except SocketError:
        print 'Cannot connect to Tor control port'
        sys.exit()

    # Create an ephemeral hidden service
    try:
        print 'Creating hidden service'
        result = c.create_hidden_service(HIDDEN_SERVICE_DIR, 80, target_port=8080)
        print " * Created host: %s" % result.hostname
        onion = result.hostname
    except UnsatisfiableRequest:
        print 'Cannot create ephemeral hidden service, Tor version is too old'
        sys.exit()
    except Exception, e:
        print e
        sys.exit()


    t.join()
if __name__ == '__main__':
    main()