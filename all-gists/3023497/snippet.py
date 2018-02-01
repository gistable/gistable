from Crypto.Cipher import AES
from StringIO import StringIO
from bplist import BPlistReader #https://github.com/farcaller/bplist-python
import M2Crypto
import gzip
import struct

def xor_strings(s, key):
    res = ""
    for i in xrange(len(s)):
            res += chr(ord(s[i]) ^ ord(key[i%len(key)]))
    return res

def aes_ctr_decrypt(data, key, iv=None, ctr=1):
    res = ""
    a = AES.new(key)
    x = a.encrypt("\x00"*8 + struct.pack(">Q", ctr))
    for i in xrange(0,len(data), 16):
        res += xor_strings(data[i:i+16], x)
        ctr += 1
        if len(data[i:i+16]) == 16:
            x = a.encrypt("\x00"*8 + struct.pack(">Q", ctr))
    return res

#use https://github.com/meeee/pushproxy to intercept
msg = BPlistReader(open("message.plist","rb").read()).parse()
d = gzip.GzipFile("", fileobj=StringIO(msg["P"].data)).read()
l = struct.unpack(">H", d[1:3])[0]
x = d[3:3+l]

#extract "iMessage encryption key" from recipient keychain
pk = M2Crypto.RSA.load_key("recipient_key.txt")

#decrypt session key
z = pk.private_decrypt(x[:160], M2Crypto.RSA.pkcs1_oaep_padding)
aes_key = z[:16]
data = z[16:] + x[160:]
#decrypt message payload
decrypted = aes_ctr_decrypt(data, aes_key)
#double gzip !!!
dec = gzip.GzipFile("", fileobj=StringIO(decrypted)).read()
p = BPlistReader(dec).parse()
print p
