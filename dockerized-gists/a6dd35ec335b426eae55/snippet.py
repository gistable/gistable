import string
import uuid

alphabet = string.digits + string.ascii_letters

def base62_encode(n):
    ret = ''
    while n > 0:
        ret = alphabet[n % 62] + ret
        n /= 62
    return ret

def url62():
    return base62_encode(uuid.uuid4().int)