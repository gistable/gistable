import shodan
import socket

# Configuration options
API_KEY = 'YOUR API KEY'
SEARCH_QUERY = 'netcam'
CONNECTION_TIMEOUT = 1.5

def is_camera(ip_str):
	"""Check whether the given IP operates a valid webcam by checking for the existence of a URL."""
	try:
		# Connect to the camera
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.settimeout(CONNECTION_TIMEOUT)
		sock.connect((ip_str,80))
		sock.send('GET /anony/mjpg.cgi HTTP/1.0\r\n\r\n')
		res = sock.recv(100)
		if(res.find('200 OK') > 0):
			return True
		return False
	except:
		return False


if __name__ == '__main__':
	# Setup the Shodan API connection
	api = shodan.Shodan(API_KEY)

	with open('cameras.txt', 'w') as fout:
		try:
			# Search Shodan for the camera and iterate over the results
			for banner in api.search_cursor(SEARCH_QUERY):
				if is_camera(banner['ip_str']):
					data = 'http://%s/anony/mjpg.cgi' % banner['ip_str']
					print(data)
					fout.write(data + '\n')
		except Exception, e:
			print('Error: %s' % str(e))
