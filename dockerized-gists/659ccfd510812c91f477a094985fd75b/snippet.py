import requests
import argparse
import os
import time

def checkkey(kee):
	try:
		if len(kee) == 64:
			return kee
		else:
			print "There is something wrong with your key. Not 64 Alpha Numeric characters."
			exit()
	except Exception, e:
			print e
			
def checkhash(hsh):
	try:
		if len(hsh) == 32:
			return hsh
		elif len() == 40:
			return hsh
		elif len(hsh) == 64:
			return hsh
		else:
			print "The Hash input does not appear valid."
			exit()
	except Exception, e:
			print e
			
def fileexists(filepath):
	try:
		if os.path.isfile(filepath):
			return filepath
		else:
			print "There is no file at:" + filepath
			exit()
	except Exception, e:
			print e

def main():
	parser = argparse.ArgumentParser(description="Query hashes against Virus Total.")
	parser.add_argument('-i', '--input', type=fileexists, required=False, help='Input File Location EX: /Desktop/Somewhere/input.txt')
	parser.add_argument('-o', '--output', required=True, help='Output File Location EX: /Desktop/Somewhere/output.txt ')
	parser.add_argument('-H', '--hash', type=checkhash, required=False, help='Single Hash EX: d41d8cd98f00b204e9800998ecf8427e')
	parser.add_argument('-k', '--key', type=checkkey, required=True, help='VT API Key EX: ASDFADSFDSFASDFADSFDSFADSF')
	parser.add_argument('-u', '--unlimited', action='store_const', const=1, required=False, help='Changes the 26 second sleep timer to 1.')
	args = parser.parse_args()

	#Run for a single hash + key
	if args.hash and args.key:
		file = open(args.output,'w+')
		file.write('Below is the identified malicious file.\n\n')
		file.close()
		VT_Request(args.key, args.hash.rstrip(), args.output)
	#Run for an input file + key
	elif args.input and args.key:
		file = open(args.output,'w+')
		file.write('Below are the identified malicious files.\n\n')
		file.close()
		with open(args.input) as o:
			for line in o.readlines():
				VT_Request(args.key, line.rstrip(), args.output)
				if args.unlimited == 1:
					time.sleep(1)
				else:
					time.sleep(26)
	
def VT_Request(key, hash, output):
	params = {'apikey': key, 'resource': hash}
	url = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
	json_response = url.json()
	print json_response
	response = int(json_response.get('response_code'))
	if response == 0:
		print hash + ' is not in Virus Total'
		file = open(output,'a')
		file.write(hash + ' is not in Virus Total')
		file.write('\n')
		file.close()
	elif response == 1:
		positives = int(json_response.get('positives'))
		if positives == 0:
			print hash + ' is not malicious'
			file = open(output,'a')
			file.write(hash + ' is not malicious')
			file.write('\n')
			file.close()
		else:
			print hash + ' is malicious'
			file = open(output,'a')
			file.write(hash + ' is malicious. Hit Count:' + str(positives))
			file.write('\n')
			file.close()
	else:
		print hash + ' could not be searched. Please try again later.'
# execute the program
if __name__ == '__main__':
	main()







