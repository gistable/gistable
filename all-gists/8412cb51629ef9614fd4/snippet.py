import urllib
import time
import hmac
import hashlib
import base64
def _sign_string(uri, key, key_name):

    '''
    100000 = milsecond expiry
    '''
    expiry = int(time.time() + 10000)

    string_to_sign = urllib.quote_plus(uri) + '\n' + str(expiry)
    print 'url: ' + uri
    print 'url encoded: ' + string_to_sign

    key = key.encode('utf-8')
    string_to_sign = string_to_sign.encode('utf-8')
    print 'url encoded: ' + string_to_sign
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    signature = signed_hmac_sha256.digest()
    signature = base64.b64encode(signature)


    return 'SharedAccessSignature sr=' + urllib.quote_plus(uri)  + '&sig=' + urllib.quote(signature) + '&se=' + str(expiry) + '&skn=' + key_name

print _sign_string('https://<Service Bus Namespace>.servicebus.windows.net/<Hub Name>/publishers/<Device Id>/messages', '<Your Shared Access Token>', '<Your Key Name>')
