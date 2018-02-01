import hashlib, zlib
HASH_BLOCKSIZE = 65536
def filebaidumd5(f, size=262144):
  h1 = hashlib.md5()
  h2 = 0
  pos = 0
  buf = f.read(min(HASH_BLOCKSIZE, size))
  md5_at_size = None
  while buf:
    pos += len(buf)
    h1.update(buf)
    h2 = zlib.crc32(buf, h2)
    if pos < size:
      buf = f.read(min(HASH_BLOCKSIZE, size - pos))
    else:
      buf = f.read(HASH_BLOCKSIZE)
      if pos == size:
        h1_clone = h1.copy()
        md5_at_size = h1_clone.hexdigest()
  if pos < size: raise ValueError('not enough data')
  return pos, h1.hexdigest(), md5_at_size, '%08x' % (h2 & 0xffffffff)

if __name__ == '__main__':
  import sys
  if len(sys.argv) < 2:
    print 'No action specified.'
    sys.exit()
  for filename in sys.argv[1:]:
    try:
      print filename, filebaidumd5(file(filename))
    except Exception, e:
      print str(e)