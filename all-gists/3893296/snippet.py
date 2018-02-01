from Crypto import HMAC, SHA256

def hmac_sha256(key, msg):
    hash_obj = HMAC.new(key=key, msg=msg, digestmod=SHA256)
    return hash_obj.hexdigest()