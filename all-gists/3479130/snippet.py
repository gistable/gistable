import math
import hashlib

def bytes_to_hex(str):
	return ''.join( [ "%02x" % ord( x ) for x in str] ).strip()

def chunk_hashes(str):
	"""
	Break up the byte-string into 1MB chunks and return sha256 hashes
	for each.
	"""
	chunk = 1024*1024
	chunk_count = int(math.ceil(len(str)/float(chunk)))
	chunks = [str[i*chunk:(i+1)*chunk] for i in range(chunk_count)]
	return [hashlib.sha256(x).digest() for x in chunks]

def tree_hash(hashes):
	"""
	Given a hash of each 1MB chunk (from chunk_hashes) this will hash
	together adjacent hashes until it ends up with one big one. So a
	tree of hashes.
	"""
	while len(hashes) > 1:
		hashes = [hashlib.sha256("".join(hashes[i:i+2])).digest() for i in xrange(0, len(hashes), 2)]
		
	return hashes[0]
	
with file('file_list.txt', 'rb') as f:
	content = f.read()
	hashes = chunk_hashes(content)
	print bytes_to_hex(tree_hash(hashes))