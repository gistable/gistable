from shodan import WebAPI
import re,socket

key = 'YOURKEYHERE'
filter = 'netcam'

def checkCam(ip):
	try:
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.settimeout(1.5)
		sock.connect((ip,80))
		sock.send('GET /anony/mjpg.cgi HTTP/1.0\r\n\r\n')
		res = sock.recv(100)
		if(res.find('200 OK') > 0):
			return True
		return False
	except:
		return False


api = WebAPI(key)

#get the first page of results
res = api.search(filter)

#keep track of how many results we have left
total_pages = (res['total']/50)+1
page = 1

outfile = open('camlog_new','w')

try:
	while(page <= total_pages):
		#check the matches to see if they fit what we are looking for
		for r in res['matches']:
			#if(r['data'].find(filter)>0):
			print 'Checking %s' % r['ip']
			if(checkCam(r['ip'])):
				print 'Found http://%s/anony/mjpg.cgi' % r['ip'] 
				f = 'http://%s/anony/mjpg.cgi\n' % r['ip']
				outfile.write(f)
				outfile.flush()
				
		page +=1
		res = api.search(filter,page)
except():
	print 'fail'
	
file.close()
