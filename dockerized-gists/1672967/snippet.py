import email.utils # for rfc2822 formatted current timestamp
import requests

class CometClient(object):

	def __init__(self, last_modified=None):
		if last_modified is None:
			self.last_modified = email.utils.formatdate()
		else:
			self.last_modified = last_modified
		self.etag = 0

	def listen(self, url):
		while True:
			self._get_request(url)

	def _get_request(self, url):
		try:
			resp = requests.get(url, headers={
					'If-None-Match': str(self.etag),
					'If-Modified-Since': str(self.last_modified)})
			self.last_modified = resp.headers['Last-Modified']
			self.etag = resp.headers['Etag']
			self.handle_response(resp.content)
		except requests.exceptions.Timeout:
			pass

	def handle_response(self, response):
		print response

if __name__ == '__main__':

	import sys
	comet = CometClient()
	comet.listen(sys.argv[1])
