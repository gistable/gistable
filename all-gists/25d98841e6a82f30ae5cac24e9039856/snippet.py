import re
import os,sys
import pefile
import struct
import zipfile
import hashlib
import StringIO
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5,AES


RSA_re = re.compile(r'RSA(1|2)')
get_urls = lambda d: map(lambda x:x.strip("\x00"),re.findall("https?://[\x1f-\x7e]{6,}\x00",d))
get_strings = lambda d: re.findall('[ -~]{3,}',d)
BTC_re = re.compile('^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$')

def get_rsc(pe,pred):
    def walk_rsc(d):
        if pred(pe,d):
            x = d.data.struct
            return pe.get_data(x.OffsetToData,x.Size)
    
        if not hasattr(d,'directory'): return None
    
        for d in d.directory.entries:
            r = walk_rsc(d)
            if r: return r
        
    for d in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        r=walk_rsc(d)
        if r:return r

def rsc_pe_pred(pe,d):
    return  hasattr(d,'data') and pe.get_data(d.data.struct.OffsetToData,  2) == 'MZ'

def rsc_zip_pred(pe,d):
    return  hasattr(d,'data') and pe.get_data(d.data.struct.OffsetToData,  2) == 'PK'


def try_passwd(zipf,f,pw):
    try:
        zp = zipfile.ZipFile(StringIO.StringIO(zipf))
        return zp.open(f,'r',pw).read()
    except Exception as e:
        return False

class RSAKEY(object):

    def __init__(self,d):
        self.bin = d
        self.off = 0 
        self.bits = 0
    def get_int(self,b):
        r=long(self.bin[self.off:self.off+self.bits/b][::-1].encode('hex'),16)
        self.off += self.bits/b
        return r

    def unpack(self):

        if self.bin[0] not in ["\x06","\x07"]:
            return None

        if self.bin[8:12] not in ['RSA1','RSA2']:
            return None
        key = {}
        priv = self.bin[0] == "\x07"
        self.bits,key['e'] = struct.unpack('II',self.bin[12:20])
        self.off = 20
        key['n']= self.get_int(8)
        if priv:
            key['p1'] = self.get_int(16)
            key['p2'] = self.get_int(16)
            key['exp1'] = self.get_int(16)
            key['exp2'] = self.get_int(16)
            key['coeff'] = self.get_int(16)
            key['d'] = self.get_int(8)
            ko = RSA.construct((key['n'],long(key['e']),key['d']))
        else:
            ko = RSA.construct((key['n'],long(key['e'])))
        return ko,key
    
def decode_aes_key(key,data):
    ## stolen from https://github.com/sysopfb/Malware_Scripts/blob/master/wannacry/decode_dll.py
    ## kudos to sysopfb
    cipher = PKCS1_v1_5.new(key)

    sentinel = Random.new().read(16)
    d = cipher.decrypt(data[::-1],sentinel)
    return d

def check_hdr(bin):
    return True


def handle_dropper(fpath):
    pe = pefile.PE(sys.argv[1])
    for s in pe.sections:
        if s.Name.startswith('.data'):
            url = get_urls(s.get_data())[0]
            print '[+] Kill-Switch/Sandbox check url',url
            break
    return get_rsc(pe,rsc_pe_pred)
try:
    inner_exe = handle_dropper(sys.argv[1])
    pe2= pefile.PE(data=inner_exe)
    print '[+] got dropper'
    drop = True
except Exception as e:
    drop= False
    pe2 = pefile.PE(sys.argv[1])
    inner_exe = open(sys.argv[1]).read()
    print '[+] got inner loader'
    
inner_zip =get_rsc(pe2,rsc_zip_pred)
cfg_files = []
for s in pe2.sections:
    if s.Name.startswith('.data'):
        data_s = s
        strings= get_strings(s.get_data())
        for st in strings:
            if BTC_re.match(st):
                print '[+] bitcoin address', st
            elif st.endswith('.wnry'):
                print '[*] possible configuration file', st
                cfg_files.append(st)
            elif st.startswith('Global'):
                print '[+] Mutex',st


# for s in cfg_files:
#     try_passwd(inner_zip,s,'')

for s in strings:
     if try_passwd(inner_zip,cfg_files[0],s):
         print '[+] zip password',s
         passwd = s
for f in cfg_files:
    d= try_passwd(inner_zip,f,passwd)
    if 'onion' in d:
        print '[+] Configuration file',f
        urls = get_strings(d)[0]
        print '[+] payment sites:\n ',
        print '\n  '.join(urls.split(';'))
    else:
        end_dll = d

off = RSA_re.finditer(inner_exe).next().start() - 8
ko,key = RSAKEY(inner_exe[off:]).unpack()
print '[+] 1st Embeded RSA key'
print ko.exportKey()
if not check_hdr(end_dll):
    print '[-] wrong file...'
    
(_, size) = struct.unpack('<IQ', end_dll[12+256:12+256+12])
aes_key = decode_aes_key(ko,end_dll[12:256+12])
c = AES.new(aes_key, AES.MODE_CBC, '\x00'*16)
core=c.decrypt(end_dll[24+256:24+256+size])

if drop:
    fname = 'inner.%s.exe' % hashlib.sha256(inner_exe).hexdigest()
    print '[+] saving inner loader as', fname
    with open('/tmp/' + fname,'w') as f:
        f.write(inner_exe)

fname = 'inner.%s.zip' % hashlib.sha256(inner_zip).hexdigest()
print '[+] saving inner zip as', fname
with open('/tmp/' + fname,'w') as f:
        f.write(inner_zip)
print '[+] embeded keys:'
for g in RSA_re.finditer(core):
    ko,_ = RSAKEY(core[g.start()-8:]).unpack()
    print ko.exportKey()

        
fname = 'core.%s.dll' % hashlib.sha256(core).hexdigest()
print '[+] saving core dll as', fname
with open('/tmp/' + fname,'w') as f:
        f.write(core)