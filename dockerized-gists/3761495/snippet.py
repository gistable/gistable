import simplejson
import json

def put(data, filename):
	try:
		jsondata = simplejson.dumps(data, indent=4, skipkeys=True, sort_keys=True)
		fd = open(filename, 'w')
		fd.write(jsondata)
		fd.close()
	except:
		print 'ERROR writing', filename
		pass

def get(filename):
	returndata = {}
	try:
		fd = open(filename, 'r')
		text = fd.read()
		fd.close()
		returndata = json.read(text)
		# Hm.  this returns unicode keys...
		#returndata = simplejson.loads(text)
	except: 
		print 'COULD NOT LOAD:', filename
	return returndata

if __name__ == '__main__':
	o = get(sys.argv[1]);
	if o:
		put(o, sys.argv[1]);
