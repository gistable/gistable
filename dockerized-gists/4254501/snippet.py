#!/usr/bin/python

import BaseHTTPServer
import SimpleHTTPServer
import os
import subprocess
import shlex
import sys
import multiprocessing
    
# You can use: 'python -m SimpleHTTPServer 8000' but that won't advertise the server via Bonjour
# This version picks a random port and advertise the server.

def main(path = '.', address = '0.0.0.0', name = 'test', type = '_http._tcp', open = True, advertise = True):
	HandlerClass = SimpleHTTPServer.SimpleHTTPRequestHandler
	ServerClass = BaseHTTPServer.HTTPServer
	protocol="HTTP/1.0"
	domain = 'local' #'.'

	os.chdir(path)
	server_address = (address, 0)

	HandlerClass.protocol_version = protocol
	httpd = ServerClass(server_address, HandlerClass)
	sa = httpd.socket.getsockname()

	thePipe = None

	try:
		#### Start the server in new process...
		theProcess = multiprocessing.Process(target=httpd.serve_forever)
		theProcess.start()

		#### Advertise the server using long living dns-sd...
		if advertise:
			theArguments = 'dns-sd -R \'%s\' \'%s\' \'%s\' %s' % (name, type, domain, sa[1])
			theArguments = shlex.split(theArguments)
			thePipe = subprocess.Popen(theArguments)

		#### Open a web browser to the server...
		if open:
			theArguments = 'open \'http://%s:%s/\'' % ('localhost', sa[1])
			theArguments = shlex.split(theArguments)
			subprocess.call(theArguments)

		print "#### Serving HTTP on", sa[0], "port", sa[1], "..."
		theProcess.join()
	except:
		raise
	finally:
		if thePipe:
			thePipe.terminate()

if __name__ == '__main__':

	args = { 'name': 'My Server' }

	# HTTPServer . 'My Server'

	if len(sys.argv) > 1:
		args['path'] = sys.argv[1]
	if len(sys.argv) > 2:
		args['name'] = sys.argv[2]
	
	main(**args)
