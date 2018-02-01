"""
Extract GlobeImposter 2.0 Ransomware Config
Author: @demonslay335
"""

import os
import sys
import binascii
import re
import hashlib
import pefile
import argparse

# https://github.com/bozhu/RC4-Python
# RC4 key scheduling
def KSA(key):
    keylength = len(key)

    S = range(256)

    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % keylength]) % 256
        S[i], S[j] = S[j], S[i]  # swap

    return S

# RC4 pseudo-random generator algorithm
def PRGA(S):
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]  # swap

        K = S[(S[i] + S[j]) % 256]
        yield K

# Use RC4 algorithm
def RC4(key):
    S = KSA(key)
    return PRGA(S)

# Decrypt using RC4
def DecryptRC4(cipher, key):
	# Generate RC4 keystream
	keystream = RC4(key)
	
	# Plaintext
	plaintext = ''
	
	# Decrypt with RC4
	for c in cipher:
		if isinstance(c, basestring):
			x = ord(c) ^ keystream.next()
		else:
			x = c ^ keystream.next()
		plaintext += chr(x)
	
	return plaintext

# Convert string to integers
def convert(s):
	return [ord(c) for c in s]

# Check for non-ASCII in string
def ascii_only(s):
	return all(ord(char) < 128 for char in s)

# Decrypt given config
def decrypt_config(config, config2, note, note2Part1, note2Part2, extra, key, key2):
	
	# Convert key and cipher to byte arrays
	key = convert(key)	
	key2 = convert(key2)
	cipher = convert(config)
	
	# Test decrypt
	testPlaintext = DecryptRC4(config, key)
	
	if not ascii_only(testPlaintext):
		# Try secondary RC4 key
		key = key2
		print "[!] Primary RC4 key failed, switching to secondary RC4 key..."

	configPlaintext = DecryptRC4(config, key)
	config2Plaintext = DecryptRC4(config2, key)
	notePlaintext = DecryptRC4(note, key)
	note2Part1Plaintext = DecryptRC4(note2Part1, key)
	note2Part2Plaintext = DecryptRC4(note2Part2, key)
	
	extraPlaintext = ''
	note2Plaintext = ''
	
	if extra is not '':
		extraPlaintext = DecryptRC4(extra, key)
	
	# Check extra is valid
	if not isinstance(extraPlaintext, str):
		extraPlaintext = ''
	
	# Note from resources may need decoded from widechar
	try:
		note2Plaintext = note2Part1Plaintext.decode('utf-16')
	except:
		pass
	
	try:
		note2Plaintext += note2Part2Plaintext.decode('utf-16')
	except:
		pass
	
	# Split up the configs
	config = configPlaintext.split(chr(0))
	config2 = config2Plaintext.split(chr(0))
	
	# Check for valid decryption
	if len(config) == 1:
		print "[-] Error decrypting config"
		config = ['0', '0']
	
	# Check config is valid
	if not isinstance(config[0], str) or not isinstance(config[1], str):
		print "[-] Error decrypting config"
		config = ['0', '0']

	# Check note is valid
	if notePlaintext.find('<h') != -1:
		note = notePlaintext
	elif note2Plaintext.find('<h') != -1:
		note = note2Plaintext
	else:
		print "[-] Error decrypting note"
		note = ''
	
	# Determine which config the filename is in
	if config[1] is not '' and ascii_only(config[1]):
		filename = config[1]
	elif config2[0] is not '' and ascii_only(config2[0]):
		filename = config2[0]
	else:
		print "[-] Error decoding filename"
		filename = ''
	
	# Extract any email addresses from the decrypted note
	emails = re.findall(r'[\w\.-]+@[\w\.-]+', note)
	
	# Extract any bitcoin addresses from the decrypted note
	bitcoins = re.findall(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b', note)
	
	# Extract any bitmessage addresses from the decrypted note
	bitmessages = re.findall(r'BM-[1-9a-km-zA-HJ-NP-Z]{32,34}', note)
	
	# Extract any Tor addresses from the decrypted note
	tors = [t.replace('href="', '') for t in re.findall('(?:https?://)?(?:www)?(\S*?\.onion)', note, re.M | re.IGNORECASE)]
	
	# Return our config
	return {
		'extension': config[0],
		'filename': filename,
		'note': note,
		'emails': set(emails),
		'bitmessage': set(bitmessages),
		'bitcoin': set(bitcoins),
		'tor': set(tors),
		'extra': extraPlaintext
	}

def load_file(path):
	# Read the whole file
	with open(path, 'rb') as f:
		content = f.read()
	return content

def extract_config(path):
	# Load file
	exe = load_file(path)
	
	exeHex = binascii.hexlify(exe)
	
	# Extract key as string
	m = re.search('([A-Z0-9]){512}', exe)
	
	key = '0'
	key2 = '0'
	
	# Check if we got a key this way
	if m == None:
		print "[-] Error extracting key"
	else:
		rsa = m.group(0)
		# Only the first 0x14 bytes are used as the RC4 key
		key = rsa[:0x14]
		# Or a SHA256
		key2 = hashlib.sha256(rsa).digest()
		print "[+] Extracted RC4 key: %s" % key
		print "[+] Extracted public RSA-%d key: %s" % (len(rsa) / 2 * 8, rsa)
		print "[+] Secondary RC4 key: %s" % binascii.hexlify(key2).upper()

	# Zero array used for filtering blank results
	z = '0' * 68
	
	config = ''
	
	# Regex for known config patterns
	config_patterns = [
		'[0]{22}(([0-9a-f]{2}){34})([0]{28})',
		'(([0-9a-f]{2}){74})([0]{12})'
	]

	# Iterate possible config patterns
	for pattern in config_patterns:
		
		matches = re.finditer(pattern, exeHex)
		
		# Iterate matches
		for m in matches:
			# Ignore empty matches or mostly-zero matches
			if m.group(1) != z and m.group(1).count('0') < 20:
				config = m.group(1)
				print "[+] Extracted encrypted config: %s" % config
				break
		
		# Check for success with this pattern
		if config is not '':
			break
	
	# Check we got a config cipher at all
	if config is '':
		print "[-] Error extracting config"
		return None

	# Regex for known config2 patterns
	config2_patterns = [
		'[0]{14}(([0-9a-f]{2}){38})([0]{20})',
		'[0]{4}(([0-9a-f]{2}){38})([0]{12})'
	]

	config2 = ''
	
	# Iterate possible config patterns
	for pattern in config2_patterns:
		
		matches = re.finditer(pattern, exeHex)

		# Iterate matches
		for m in matches:
			# Ignore empty matches or mostly-zero matches
			if m.group(1) != z and m.group(1).count('0') < 20:
				config2 = m.group(1)
				print "[+] Extracted encrypted secondary config: %s" % config2
				break
		
		# Check for success with this pattern
		if config2 is not '':
			break
	
	# Check we got a config2 cipher at all
	if config2 is '':
		print "[-] Error extracting secondary config"
	
	# Find potential ransom note cipher after the imports
	offset = exe.find("CommandLineA")
	
	if offset == -1:
		# Try again with another known import
		offset = exe.find("RPCRT4.dll")
		if offset == -1:
			print "[-] Error extracting note"
		else:
			offset += len("RPCRT4.dll") + 2
	else:
		offset += len("CommandLineA") + 1
	
	endOffset = offset
	
	# Search for the end of the encrypted note
	while not (ord(exe[endOffset]) == 0x00 and ord(exe[endOffset+1]) == 0x00 and ord(exe[endOffset+2]) == 0x00):
		endOffset += 1
	
	note = exe[offset:endOffset+1]
	
	# Check we got a valid note
	if note is '':
		print "[-] Error extracting note"
	else:
		print "[+] Extracted encrypted note (%d bytes)" % len(note)
	
	# Extract a secondary note that could be in the resources
	pe = pefile.PE(path)
	
	note2Part1 = ''
	note2Part2 = ''
	plaintextExtension = ''
	plaintextFilename = ''
	extra = ''
	
	offset = 0x0
	size = 0x0
	
	# Iterate resources
	if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
		for rsrc in pe.DIRECTORY_ENTRY_RESOURCE.entries:
			# Iterate resource entries
			for entry in rsrc.directory.entries:
				# Get offset and size of the resource
				offset = entry.directory.entries[0].data.struct.OffsetToData
				size = entry.directory.entries[0].data.struct.Size
				# Check for entry 101, some random extra data possibly of interest
				if entry.id == 101:
					extra = pe.get_memory_mapped_image()[offset:offset+size]
					print "[+] Extracted extra data from resources: %s" % binascii.hexlify(extra)
				# Check for entry 104, part 1 of note
				if entry.id == 104:
					note2Part1 = pe.get_memory_mapped_image()[offset:offset+size]
					print "[+] Extracted part 1 of encrypted note from resources (%d bytes)" % len(note2Part1)
				# Check for entry 105, part 2 of note
				elif entry.id == 105:
					note2Part2 = pe.get_memory_mapped_image()[offset:offset+size]
					print "[+] Extracted part 2 of encrypted note from resources (%d bytes)" % len(note2Part2)
				# Check for entry 106, public RSA key and RC4 key
				elif entry.id == 106:
					rsa = pe.get_memory_mapped_image()[offset:offset+size]
					key = rsa[:0x14]
					print "[+] Extracted RC4 key from resources: %s" % key
					print "[+] Extracted public RSA-%d key: %s" % (len(rsa) / 2 * 8, rsa)
				# Check for entry 110, plaintext extension
				elif entry.id == 110:
					plaintextExtension = pe.get_memory_mapped_image()[offset:offset+size]
					print "[+] Extracted plaintext extension from resources"
				# Check for entry 111, plaintext ransom note filename
				elif entry.id == 111:
					plaintextFilename = pe.get_memory_mapped_image()[offset:offset+size]
					print "[+] Extracted plaintext ransom note filename from resources"

	# Decrypted config
	decrypted = decrypt_config(config.decode('hex'), config2.decode('hex'), note, note2Part1, note2Part2, extra, key, key2)
	
	# Check for successful decryption
	if decrypted is not None:
		ret = decrypted.copy()
		
		# Check for plaintext extension (from resources)
		if plaintextExtension is not '':
			# Overwrite
			ret.update({'extension': plaintextExtension})
		
		# Check for plaintext ransom note filename (from resources)
		if plaintextFilename is not '':
			# Overwrite
			ret.update({'filename': plaintextFilename})
	
	else:
		return None
	
	return ret

# Setup argument parts
parser = argparse.ArgumentParser(description='Extract configuration from GlobeImposter 2.0 ransomware.')
parser.add_argument('file', help='executable path')
parser.add_argument('-n, --note', dest='note', help='output ransom note contents', action='store_true')
parser.add_argument('-s, --save_note', dest='save_note', help='save ransom note contents to file', action='store_true')

# Parse arguments
args = parser.parse_args()

# Extract config for given binary
config = extract_config(args.file)

# Check for success
if config == None:
	print "\n[-] Error decrypting config"
else:
	# Output config data
	print (
		"\n[+] Extension: %s"
		"\n[+] Ransom Note Filename: %s"
		% (config['extension'], config['filename'])
	)
	
	# Output extra data if applicable
	if config['extra'] is not '':
		print "[+] Extra data: %s" % config['extra']
	
	# Output emails, etc.
	for e in config['emails']:
		print "[+] Email Address: %s" % e
	for b in config['bitmessage']:
		print "[+] BitMessage: %s" % b
	for b in config['bitcoin']:
		print "[+] Bitcoin: %s" % b
	for t in config['tor']:
		print "[+] Tor: %s" % t
	
	# Check for saving the note
	if args.save_note:
		note_path = os.path.join(os.path.dirname(args.file), config['filename'] + ' - ' + os.path.basename(args.file))
		with open(note_path, 'wb') as f:
			f.write(config['note'])
		print "[+] Wrote ransom note contents to: %s" % note_path
	# Or outputting it
	elif args.note:
		print "[+] Note:\n%s" % config['note'].encode(sys.stdout.encoding, errors='replace')