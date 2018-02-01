"""
Extract BTCWare Ransomware Config
Author: @demonslay335
"""

import sys
import string
import re
import os
import argparse

# https://stackoverflow.com/a/17197027/1301139
def strings(filename, min=4, max=10000):
    with open(filename, "rb") as f:           # Python 2.x
        result = ""
        for c in f.read():
            if c in string.printable:
                result += c
                continue
            if len(result) >= min and len(result) <= max:
                yield result
            result = ""
        if len(result) >= min and len(result) <= max:  # catch result at EOF
            yield result

# Double-check it is an executable
def isexe(path):
	with open(path, 'rb') as f:
		return f.read()[:2] == 'MZ'

# Check if file appears to be packed
def ispacked(path):
	# Iterate strings
	for s in strings(path, 4, 10):
		# UPX packing
		if 'UPX0' in s or 'UPX1' in s:
			return True
	return False

# Check if this is just a decrypter
def isdecrypter(path):
	# Iterate strings
	for s in strings(path, 10):
		# Decrypt import
		if 'Decrypt %s' in s or 'Decrypt start in' in s:
			return True
	return False

# Extract config from file
def extract_config(exe):
	note_path = ''
	
	decrypter = isdecrypter(exe)
	key = ''
	extension = ''
	note_filename = ''
	note_contents = ''
	emails = []
	
	# Iterate strings
	for s in strings(exe, 7):
		# AES key (decrypter)
		if decrypter and re.match(r"[A-F0-9]{64}", s):
			key = s
		# RSA key
		elif 'BEGIN PUBLIC KEY' in s:
			key = s
		# Note filename
		elif '.txt' in s or '.hta' in s or '.inf' in s:
			note_filename = s
		# Extension for decrypter
		elif decrypter and '%' not in s and re.match(r"^\.[a-z]{4,10}$", s):
			extension = s
		# Extension (exception for key.dat file and exe name)
		elif not decrypter and '%s' in s and '.' in s and 'key' not in s and 'exe' not in s and 'Decrypt' not in s:
			extension = s
		# Email address
		elif re.match(r"[^@]+@[^@]+\.[^@]+", s):
			matches = re.findall(r'[\w\.-]+@[\w\.-]+', s)
			for match in matches:
				emails.append(match)
			# May also be the HTML
			if '<' in s and '>' in s and 'manifest' not in s:
				note_contents += s
		# HTML
		elif '<' in s and '>' in s and 'manifest' not in s:
			note_contents += s
		# Try base64 decoding a string
		try:
			b = s.decode("base64").decode("ascii")
			# Check for success
			if len(b) > 0:
				# Email address
				if re.match(r"[^@]+@[^@]+\.[^@]+", b):
					matches = re.findall(r'[\w\.-]+@[\w\.-]+', b)
					for match in matches:
						emails.append(match)
				# May also be the HTML
				if '<' in b and '>' in b and 'manifest' not in b:
					note_contents += b
		except:
			continue
	
	return {
		'decrypter': decrypter,
		'key': key,
		'extension': extension,
		'note_filename': note_filename,
		'emails': set(emails),
		'note_contents': note_contents
	}

def process_file(path, args, output=True):
	# Verify it is a file and executable
	if not os.path.isfile(path) or not isexe(path):
		return
	
	# Check for packing
	if ispacked(path):
		print "[-] File appears to be packed"
		return
	
	# Extract config
	config = extract_config(path)
	
	# Check for success
	if config is None:
		print "[-] Error extracting config"
		return
	
	# Output our config
	if output:
		print "File: %s" % path
		if not config['decrypter']:
			if args.only is None or args.only == 'key':
				print "[+] RSA Key: %s" % config['key']
			if args.only is None or args.only == 'extension':
				print "[+] Extension: %s" % config['extension']
			if args.only is None or args.only == 'note':
				print "[+] Ransom Note: %s" % config['note_filename']
			if args.only is None or args.only == 'email':
				for e in config['emails']:
					print "[+] Email Address: %s" % e
		else:
			print "[!] File is a decrypter"
			if args.only is None or args.only == 'key':
				print "[+] AES key: %s" % config['key']
			if args.only is None or args.only == 'extension':
				print "[+] Extension: %s" % config['extension']
	
	# Check for saving the note
	if args.save_note:
		note_path = os.path.join(os.path.dirname(path), config['note_filename'] + ' - ' + os.path.basename(path))
		with open(note_path, 'ab') as f:
			f.write(config['note_contents'])
		print "[+] Wrote ransom note contents to: %s" % note_path
	# Or outputting it
	elif args.note or args.only == 'note':
		if output:
			print config['note_contents']
	
	if output:
		print ""

	return config

def process_unique(configs, args):
	# Iterate and create unique sets
	keys = set()
	extensions = set()
	notes = set()
	emails = set()
	for config in configs:
		keys.add(config['key'])
		extensions.add(config['extension'])
		notes.add(config['note_filename'])
		emails.update(config['emails'])
	# Filter empties
	keys = filter(None, keys)
	extensions = filter(None, extensions)
	notes = filter(None, notes)
	emails = filter(None, emails)
	
	print "[+] Analyzed %d samples..." % len(config)
	if args.only is None or args.only == 'key':
		print "[+] Unique RSA Keys (%d): " % len(keys)
		for key in keys:
			print key
	if args.only is None or args.only == 'extension':
		print "[+] Unique Extensions (%d): " % len(extensions)
		for extension in extensions:
			print extension
	if args.only is None or args.only == 'note':
		print "[+] Unique Ransom Notes (%d): " % len(notes)
		for note in notes:
			print note
	if args.only is None or args.only == 'email':
		print "[+] Unique Email Addresses (%d): " % len(emails)
		for email in emails:
			print email

# Setup argument parser
parser = argparse.ArgumentParser(description='Extract configuration from BTCWare ransomware.')
parser.add_argument('path', help='executable path or folder')
parser.add_argument('-n, --note', dest='note', help='output ransom note contents', action='store_true')
parser.add_argument('-s, --save_note', dest='save_note', help='save ransom note contents to file', action='store_true')
parser.add_argument('-u, --unique', dest='unique', help='output only unique config variables', action='store_true')
parser.add_argument('-o, --only', dest='only', help='only output certain variable',
	choices=['key', 'email', 'extension', 'note'])

# Parse arguments
args = parser.parse_args()

# Check for path
if os.path.isdir(args.path):
	configs = []
	# Iterate files
	for root, dirs, files in os.walk(args.path):
		for filename in files:
			# Process the file
			config = process_file(os.path.join(root, filename), args, not args.unique)
			# Add to config array
			if config is not None:
				configs.append(config)
	# Unique flag
	if args.unique:
		# Process configs as unique
		process_unique(configs, args)
	
# Check for file
elif os.path.isfile(args.path):
	# Process the file
	process_file(args.path, args)
else:
	print "[-] Invalid executable"