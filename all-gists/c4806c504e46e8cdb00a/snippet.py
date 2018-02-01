import os
import base64
import json
from Crypto.Cipher import AES
from phpserialize import loads


def decrypt(payload):
    data = json.loads(base64.b64decode(payload))

    value =  base64.b64decode(data['value'])
    iv = base64.b64decode(data['iv'])

    return unserialize(mcrypt_decrypt(value, iv))

def mcrypt_decrypt(value, iv):
    AES.key_size=128
    key=os.environ['APP_KEY']

    crypt_object=AES.new(key=key,mode=AES.MODE_CBC,IV=iv)
    return crypt_object.decrypt(value)

def unserialize(serialized):
    return loads(serialized)