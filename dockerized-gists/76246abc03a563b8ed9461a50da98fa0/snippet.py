import sys
import hashlib
import struct 
import requests

def decode(data,seed,step):
    r = []
    k = seed
    for c in map(ord,data):
        r.append(chr(c ^ k))
        k = (k + step) % 256
    return ''.join(r)


d = requests.get(sys.argv[1]).content
if not d:
    print '[-] nope, no locky here'
    sys.exit(1)
cksum = struct.unpack('I',d[-4:])[0]    
d = d[:-4][::-1]
seed = ord(d[0]) ^ ord('M')
step = (ord(d[1]) ^ ord('Z')) - seed
exe = decode(d,seed,step)
pe_off = struct.unpack('H',exe[0x3c:0x3c+2])[0]
if len(exe) > pe_off and exe[pe_off] == 'P' and exe[pe_off+1] == 'E':
    fname = hashlib.sha256(exe).hexdigest()
    print '[+] decoded with seed: %d and step: %d' % (seed,step)
    print '[+] saving as %s.exe' % fname
    with open(fname+'.exe','w') as f:
        f.write(exe)
else:
    print '[-] nope, sorry world changed'

