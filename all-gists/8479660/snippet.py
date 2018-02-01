import urllib
import urllib2
import xml.etree.ElementTree as ET
import datetime

class hamqth:
	username = None
	password = None
	session_id = None
	session_id_timestamp = datetime.datetime.now()
	ns = '{http://www.hamqth.com}'
	
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.get_session_id()
		
	def get_session_id(self):
		td = datetime.datetime.now() - self.session_id_timestamp
		if td.total_seconds() > 3300 or self.session_id is None:
			login = {'u' : self.username, 'p' : self.password}
			try:
				response = urllib2.urlopen('http://www.hamqth.com/xml.php?' + urllib.urlencode(login))
			except URLError as e:
				print e.reason
				return
			else:
				xml = response.read()
				root = ET.fromstring(xml)
				self.session_id = root.find(self.ns + 'session/' + self.ns + 'session_id').text
				if self.session_id is None:
					print 'Could not get session_id'
				else:
					self.session_id_timestamp = datetime.datetime.now()
		
	def callbook(self, callsign):
		self.get_session_id()
		self.callsign = callsign
		query = {'id' : self.session_id, 'callsign' : callsign, 'prg' : 'Etherkit'}
		try:
			response = urllib2.urlopen('http://www.hamqth.com/xml.php?' + urllib.urlencode(query))
		except URLError as e:
			print e.reason
			return
		else:
			xml = response.read()
			root = ET.fromstring(xml)
			#ET.dump(root)
			search = root.find(self.ns + 'search')
			if search is None:
				print 'Could not find callsign'
				return
			else:
				profile = {}
				for child in search:
					profile[child.tag.replace(self.ns, '')] = child.text
				return profile