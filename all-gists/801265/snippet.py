#!/usr/bin/python
import sys
import syck as yaml
import time
from hashlib import sha1
from M2Crypto.RSA import load_pub_key, load_key
from stompy.simple import Client

# Change these.
PREFIX = 'mcollective'
CERTNAME = 'certificate-name'
s = Client('stomp.server')
s.connect('stompusername','stomppassword')
rr = load_key('path-to-unencrypted-private-key.pem')

target = '/topic/%s.discovery.command' % PREFIX
target_reply = '/topic/%s.discovery.reply' % PREFIX
s.subscribe(target_reply)
rid = sha1(str(time.time())).hexdigest()

# Put together message.
r = {}
r[':msgtime'] = int(time.time())
r[':filter'] = {
    'identity': [],
    'fact': [],
    'agent': [],
    'cf_class': [],
}
r[":requestid"] = rid
r[":callerid"] = 'cert=%s' % CERTNAME
r[":senderid"] = 'pythontest'
r[":msgtarget"] = target
r[':body'] = yaml.dump('ping')
h = rr.sign(sha1(r[':body']).digest(), 'sha1')
r[':hash'] = h.encode('base64').replace("\n", "").strip()

data = yaml.dump(r)
s.put(data, target)
time.sleep(2)
results = []
while True:
    x = None
    try:
        x = s.get_nowait()
        print x
    except:
        break
    if not x:
        break
    y = yaml.load(x.body)
    print y
    if y[':requestid'] == rid:
        results.append(y)

print [q[':senderid'] for q in results]