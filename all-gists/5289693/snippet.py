"""Attempt to solve the xkcd Alma Mater challenge.

Dependencies:
	pyskein
	requests

Usage:
	python code.py york.ac.uk
"""

import sys
import random
import string
from skein import skein1024
import requests

try:
	institution = sys.argv[1]
except:
	print("Institution name not given.")
	sys.exit(1)

# Get a list of letters to build our string out of
letters = list(string.printable + string.whitespace)
numbers = [ str(i) for i in range(0,10) ]

def random_bytes(minlen=1, maxlen=30):
	"""Generate a random byte string between the two lengths.

	:param minlen: The minimum length of the string (inclusive)
	:param maxlen: The maximum length of the string (inclusive)
	"""

	out = ''
	for i in range(0, random.randint(minlen, maxlen)):
		out += random.choice(numbers)
	return out



def submit_to_xkcd(bytes):
	"""Submit the bytestring to xkcd
	"""

	r = requests.post("http://almamater.xkcd.com/?edu=" + institution,
			{"hashable": bytes})
	print(r.text)
	# The hash supplied by xkcd
xkcdhash = "5b4da95f5fa08280fc9879df44f418c8f9f12ba424b7757de02bbdfbae0d4c4fdf9317c80cc5fe04c6429073466cf29706b8c25999ddd2f6540d4475cc977b87f4757be023f19b8f4035d7722886b78869826de916a79cf9c94cc79cd4347d24b567aa3e2390a573a373a48a5e676640c79cc70197e1c5e7f902fb53ca1858b6"

best = 418
pre = ""
try:
	while True:
		x = random_bytes() 
		h = skein1024()
		val = pre + str(x)
		#x = random_bytes()
		h.update(val.encode())
		diff = int(h.hexdigest(),16) ^ int(xkcdhash,16)
		diffbits = bin(diff).count("1")
		if(diffbits < best):
			print()
			print("New best: {} ({})".format(h.hexdigest(), diffbits))
			best = diffbits 
			print(val + "->" + str(diffbits))
			submit_to_xkcd(val)
			print("\n")


except KeyboardInterrupt:
	print("Finished.")
