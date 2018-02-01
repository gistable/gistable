import base64
import time
import OpenSSL

from django.utils import simplejson

def _json_dumps(obj):
    return simplejson.dumps(obj, separators=(',', ':'))

def _base64url(data):
    return base64.urlsafe_b64encode(data).rstrip('=')

class JWT(object):
    """Class to construct the JSON Web Tokens for authenticating
    with Google servers."""
    def __init__(self, key_file, password='notasecret'):
        # Read the key_file into memory:
        fp = file(key_file, 'rb')
        key_data = fp.read()
        fp.close()

        self._header = _base64url(_json_dumps(dict(alg='RS256', typ='JWT')))
        self._key = OpenSSL.crypto.load_pkcs12(key_data, password).get_privatekey()

    def make_claim(self, client_id, scope, lifetime=None):
        now = long(time.time())
        if lifetime is None or lifetime > 3600 or lifetime < 1:
            lifetime = 3600

        claim = _base64url(_json_dumps({
            'iss': client_id,
            'scope': scope,
            'aud': 'https://accounts.google.com/o/oauth2/token',
            'exp': now + lifetime,
            'iat': now,
        }))

        # Sign message:
        msg = '%s.%s' % (self._header, claim)
        sig = _base64url(OpenSSL.crypto.sign(self._key, msg, 'sha256'))

        return '%s.%s' % (msg, sig)
