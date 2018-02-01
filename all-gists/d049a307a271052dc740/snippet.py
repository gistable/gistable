import sys
import pefile
from StringIO import StringIO
from Crypto.Cipher import AES

K =''.join((chr(x) for x in range(15,0x4f,2)))
ENC_HEADER="\x23\x59\x90\x70\xe9\xc1\xec\x82\xb4\x87\xb3\x4e\x03\x10\x6c\x2e"
decrypt = lambda d: AES.new(K,AES.MODE_ECB).decrypt(d)
chunks = lambda l, n: [l[x: x+n] for x in xrange(0, len(l), n)]
IDX = 0
def decrypt_payload(d,off):
    global IDX
    out = StringIO()
    if decrypt(d[off:off+16]).startswith('MZ'):
        print '[%d][+] found encrypted MZ  @ %X'% (IDX,off)
    try:
        pe_hdr = decrypt(d[off:off+0x400])
        pe = pefile.PE(data=pe_hdr)
    except:
        return None

    print '[%d][+] OK its parsable, lets proceed' % IDX
    for c in chunks(d[off:],16):
        out.write(decrypt(c))
    IDX +=1
    return out


path = sys.argv[1]
#off  = int(sys.argv[2],16)
#size = int(sys.argv[3],16)
#cnt = 0 

with open(path) as f:
    d=f.read()
    
off =d.find(ENC_HEADER)    
while off != -1:
    r= decrypt_payload(d,off)
    if not r:
        print '[-] this is not a PE i was looking for...'
        sys.exit(1)
    d = r.getvalue()
    off =d.find(ENC_HEADER)    

with open(path+'.dec','wb') as f:
    f.write(d)
print '[*] decrypted payload saved as',path+'.dec'
