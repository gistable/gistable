import sampy
import urlparse
import os

def ds9echo(response):
	print response

class Client(sampy.SAMPIntegratedClient):

	def __init__(self,
			name="VAO Python Client",
			description="An interactive SAMP client for Python by the Virtual
                        Astronomical Observatory",
                        version="0.0.1"):
		self.metadata = {"samp.name": name, "samp.description.text": description, "client.version": version}
		sampy.SAMPIntegratedClient.__init__(self)
		self.do_close_hub = False
		if len(self.hub.getRunningHubs()) == 0:
			self.samp_hub = sampy.SAMPHubServer()
			self.samp_hub.start()
			self.do_close_hub = True
		self.connect()
		self.declareMetadata(self.metadata)
	
	def set(self, cmd, url=""):
		message = {"samp.mtype": "ds9.set", "samp.params":{"cmd": cmd, "url":url}}
		self.callAll("vaods9set", message)
		
	def get(self, cmd, url="", tag="vaods9get", function=ds9echo):
		self.bindReceiveResponse(tag, self.handler_wrapper)
		self.handler = function
		message = {"samp.mtype": "ds9.get", "samp.params":{"cmd": cmd, "url":url}}
		self.callAll(tag, message)

	def get_now(self, cmd, url="", tag="vaods9getnow", timeout=1000):
		message = {"samp.mtype": "ds9.get", "samp.params":{"cmd": cmd, "url":url}}
		try:
			response = self.callAndWait(self.ds9_hook, message, timeout)
			return response['samp.result']['value']
		except:
			pass

	def basic_handler(self, private_key, sender_id, msg_id, response):
		self.last_response = response['samp.result']['value']
		
	def basic_get(self, cmd, url=""):
		self.bindReceiveResponse("vaods9basicget", self.basic_handler)
		message = {"samp.mtype": "ds9.get", "samp.params":{"cmd": cmd, "url":url}}
		self.callAll("vaods9basicget", message)

	def cleanup(self):
		self.disconnect()
		print "client disconnected"
		if self.do_close_hub:
			self.samp_hub.stop()

	def handler_wrapper(self, private_key, sender_id, msg_id, response):
		ds9response = response['samp.result']['value']
		self.handler(ds9response)

	def send(self, mtype, file_id, file_path):
		self.file_path = file_path
		message = {'samp.mtype': mtype,'samp.params': {'name': file_id, 'url': self.file_url}}
		self.callAll("vaods9send", message)

	def send_votable(self, name, file_path):
		self.send('table.load.votable', name, file_path)

	def send_fits_image(self, name, file_path):
		self.send('image.load.fits', name, file_path)
		
	def send_fits_table(self, name, file_path):
		self.send('table.load.fits', name, file_path)

	@property
	def file_url(self):
		url = urlparse.urlparse(self.file_path)
		if url.scheme == '' :
			abspath = os.path.abspath(self.file_path)
			return 'file://'+abspath
		return self.file_path

	@property
	def ds9_hook(self):
		ds9_candidates = self.getSubscribedClients("ds9.get")
		if(len(ds9_candidates)==1):
			return ds9_candidates.keys()[0]
		if(len(ds9_candidates)>=2):
			print "Warning, more than one instance of DS9 found"
			return ds9_candidates.keys()[0]
		print "Error, couldn't find any DS9 instances running"
		
