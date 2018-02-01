# Detailed explanation at http://hitesh.in/2011/running-a-bottle-py-app-on-dreamhost/

#1. Add current directory to path, if isn't already 
import os, sys
cmd_folder = os.path.dirname(os.path.abspath(__file__))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import bottle
from bottle import route, run

#2. Define needed routes here	
@route('/')
def index():
	return "it works!"

	
#3. setup dreamhost passenger hook
def application(environ, start_response):
    return bottle.default_app().wsgi(environ,start_response)	

#4. Main method for local developement	
if __name__ == "__main__":
    bottle.debug(True)
    run(reloader=True)
