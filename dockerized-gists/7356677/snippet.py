#!/usr/var/env python
import sys

def convert_To_18(id):
	#check valid input
	if id is None:
		return id
	if len(id) < 15:
		print "not a valid 15 digit ID"
		return
	#print initial id
	print "15 digit ID: ", id
	suffix = ''
	for i in xrange(0, 3):
		flags = 0
		for x in xrange(0,5):
			c = id[i*5+x]
			#add flag if c is uppercase
			if c.upper() == c and c >= 'A' and c <= 'Z':
				flags = flags + (1 << x)
		if flags <= 25:
			suffix = suffix + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[flags]
		else:
			suffix = suffix + '012345'[flags - 26]
	print "18 digit ID: ",  id + suffix
	
def main():
	#exampleid = '500A000000D34Xf'
	id = str(sys.argv[1])
	
	convert_To_18(id)
	
if __name__ == "__main__":
	main()