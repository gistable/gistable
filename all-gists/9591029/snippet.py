import hashlib
import sys
from functools import partial

def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def sha1sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.sha1()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

if sys.argv[1] == 'md5':
    print(md5sum(sys.argv[2]))
elif sys.argv[1] == 'sha1':
    print(sha1sum(sys.argv[2]))
