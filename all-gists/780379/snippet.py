import urllib
import urllib2
import socket

from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from google.appengine.ext import db
from models import Status, Service, Event
from datetime import datetime, timedelta, date


results = {}
servers = [
	{
		"service": "a_server",
		"url": "http://aserver.com"
	},
	{
		"service": "another_server",
		"url": "http://anotherserver.com"
	}
]

def serverisup (service):
	# Create a new event with the given status and given service
	service = Service.get_by_slug(service)
	status = Status.get_by_slug("up")        

	e = Event(service=service, status=status, message="The server is responding.")
	e.put()

	
def serverisdown (service):
	# Create a new event with the given status and given service
	service = Service.get_by_slug(service)
	status = Status.get_by_slug("down")        

	e = Event(service=service, status=status, message="The server could not be reached")
	e.put()
	

def check(service,url):
	print "Checking " + service + " (" + url + ")..."
	
	try:
		results[service] = urlfetch.fetch(url, headers = {'Cache-Control' : 'max-age=30'}, deadline=30 )
		
	except urlfetch.Error:
		serverisdown(service)
	
	except DownloadError:
		serverisdown(service)
		
	else:
		if results[service].status_code == 500:
			serverisdown(service)
		else:
			serverisup(service)


for row in servers:
	check(row['service'],row['url'])