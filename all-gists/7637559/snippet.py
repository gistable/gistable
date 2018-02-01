#!/usr/bin/python
import hashlib, time
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

url = 'https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.10.1.tar.gz'
md5sum_expected = '3a04aa2b32c76c83725ed4d9918e362e'
response = urlopen(url)
##import pdb; pdb.set_trace()
socket = getattr(response.fp, 'raw', response.fp)._sock

# If you set this to False, you get SSLError exceptions.
# If you set this to True, you get truncated downloads that fail md5sum checks.
socket.suppress_ragged_eofs = False

data = b''
while True:
    chunk = socket.recv(8192)
    print("%d %d" % (len(chunk), len(data) + len(chunk)))
    if not chunk:
        break
    data += chunk
md5sum_actual = hashlib.md5(data).hexdigest()
filename = 'r%d' % time.time()
if md5sum_actual == md5sum_expected:
    print("OK")
    open(filename + '.ok', 'wb').write(data)
else:
    print("BAD: %s" % md5sum_actual)
    open(filename + '.bad', 'wb').write(data)
print("downloaded %d bytes" % len(data))
