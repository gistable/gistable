from Crypto.Cipher import DES3

def _make_des3_encryptor(key, iv):
    encryptor = DES3.new(key, DES3.MODE_CBC, iv)
    return encryptor


def des3_encrypt(key, iv, data):
    encryptor = _make_des3_encryptor(key, iv)
    pad_len = 8 - len(data) % 8 # length of padding
    padding = chr(pad_len) * pad_len # PKCS5 padding content
    data += padding
    return encryptor.encrypt(data)


def des3_decrypt(key, iv, data):
    encryptor = _make_des3_encryptor(key, iv)
    result = encryptor.decrypt(data)
    pad_len = ord(result[-1])
    result = result[:-pad_len]
    return result
