import urllib2
import json
import datetime

def find_start_time(datas, identifier):
	if datas.has_key('data'):
		if datas['data'].has_key('entry'):
			if datas['data']['entry'].has_key('stopTimes'):
				for stopTime in datas['data']['entry']['stopTimes']:
					if stopTime['tripId'] == identifier:
						if stopTime.has_key('predictedArrivalTime'):
							return datetime.datetime.fromtimestamp(stopTime['predictedArrivalTime'])
						else:
							return datetime.datetime.fromtimestamp(stopTime['arrivalTime'])

def delta(time):
	time_delta = time - datetime.datetime.now()
	return time_delta.seconds / 60

def convert_name(route_id):
	route_id = route_id.replace('BKK_', '')
	if route_id[-1] == u'0':
		route_id = route_id[:-1]
	elif route_id[-1] == u'1':
		route_id = route_id[:-1] + 'A'
	return route_id

def print_times():
	socket = urllib2.urlopen("http://futar.bkk.hu/0/m/ad?stopId=BKK_F00940&minutesAfter=30");
	datas = json.load(socket)

	if datas.has_key('data'):
		if datas['data'].has_key('references'):
			if datas['data']['references'].has_key('trips'):
				for trip in datas['data']['references']['trips']:
					print "%s %s: %s" % (convert_name(trip['routeId']), trip['tripHeadsign'], delta(time=find_start_time(datas=datas, identifier=trip['id'])))

print_times()
