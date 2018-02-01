# by fcicq (fcicq at fcicq dot net) @ 2012.5.12, Released under GPLv2
import hashlib
try:
  from cStringIO import StringIO
except ImportError:
  from io import BytesIO as StringIO
if bytes != str: ord = int
class ed2kHash():
  CHUNK_SIZE = 9728000
  BLOCK_SIZE = 262144
  chunkmd4_list = None
  chunkmd4 = None
  chunkpos = 0

  def __init__(self, string=b''):
    self.chunkmd4 = self._md4(string) # I know it will raise ImportError... :D
    self.chunkmd4_list = []

  def _md4(self, string=b''):
    if bytes != str and isinstance(string, str):
      string = string.decode('utf-8')
    return hashlib.new('md4', string)

  def _tohex(self, string=''):
    return ''.join(["%02x"%ord(x) for x in string])

  def update(self, string=b''):
    l = len(string)
    s = StringIO(string)
    pos = 0
    if not l: return
    while pos < l:
      blocksize = min(self.CHUNK_SIZE - self.chunkpos, l - pos, self.BLOCK_SIZE)
      self.chunkmd4.update(s.read(blocksize))
      pos += blocksize
      self.chunkpos += blocksize
      if self.CHUNK_SIZE == self.chunkpos: # filled just now
        self.chunkmd4_list.append(self.chunkmd4.digest())
        self.chunkmd4 = self._md4()
        self.chunkpos = 0
    s.close()

  def digest(self):
    if self.chunkmd4_list: # If the first block is not completed, just return the md4 result.
      return self._md4(b''.join(self.chunkmd4_list) + self.chunkmd4.digest()).digest()
    else:
      return self.chunkmd4.digest()

  def hexdigest(self):
    return self._tohex(self.digest())

  def copy(self):
    raise NotImplementedError

import sys, os
HASH_BLOCKSIZE = 262144

def filehash(f, h=None):
  if h is None:
    h = hashlib.md5()
  buf = f.read(HASH_BLOCKSIZE)
  while buf:
    h.update(buf)
    buf = f.read(HASH_BLOCKSIZE)
  return h.hexdigest()

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('No action specified.')
    sys.exit()

  for filename in sys.argv[1:]:
    try:
      base = os.path.basename(filename)
      size = os.path.getsize(filename)
      ed2k = filehash(open(filename,'rb'), ed2kHash())
      print('ed2k://|file|%s|%s|%s|/' % (base, size, ed2k))
    except Exception as e:
      print(str(e))