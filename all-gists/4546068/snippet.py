from binascii import hexlify, unhexlify
from hashlib import md5
from Crypto.Cipher import AES
try:
    from M2Crypto import EVP
except ImportError:
    EVP = None


def m2_encrypt(plaintext, key, iv, key_as_bytes=False, padding=True):
    cipher = EVP.Cipher(alg="aes_256_cbc", key=key, iv=iv,
                        key_as_bytes=key_as_bytes, padding=padding, op=1)
    return cipher.update(plaintext) + cipher.final()

def m2_decrypt(ciphertext, key, iv, key_as_bytes=False, padding=True):
    cipher = EVP.Cipher(alg="aes_256_cbc", key=key, iv=iv,
                        key_as_bytes=key_as_bytes, padding=padding, op=0)
    return cipher.update(ciphertext) + cipher.final()


def py_encrypt(plaintext, key, iv, key_as_bytes=False, padding=True):
    if key_as_bytes:
        key = bytes_to_key(key)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if padding:
        plaintext = pkcs7_encode(plaintext)
    return cipher.encrypt(plaintext)

def py_decrypt(ciphertext, key, iv, key_as_bytes=False, padding=True):
    if key_as_bytes:
        key = bytes_to_key(key)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    if padding:
        plaintext = pkcs7_decode(plaintext)
    return plaintext


def pkcs7_encode(text, k=16):
    n = k - (len(text) % k)
    return text + unhexlify(n * ("%02x" % n))

def pkcs7_decode(text, k=16):
    n = int(hexlify(text[-1]), 16)
    if n > k:
        raise ValueError("Input is not padded or padding is corrupt")
    return text[:-n]

def bytes_to_key(data, salt="12345678"):
    # Simplified version of M2Crypto.m2.bytes_to_key(). Based on:
    # https://github.com/ajmirsky/M2Crypto/blob/master/M2Crypto/EVP.py#L105
    # http://stackoverflow.com/questions/8008253/c-sharp-version-of-openssl-evp-bytestokey-method
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    key += md5(key + data).digest()
    return key


def test_pycrypto(plaintext, key, iv, key_as_bytes, padding):
    ciphertext = py_encrypt(plaintext, key, iv, key_as_bytes, padding)
    assert py_decrypt(ciphertext, key, iv, key_as_bytes, padding) == plaintext
    return ciphertext

def test_m2crypto(plaintext, key, iv, key_as_bytes, padding):
    ciphertext = m2_encrypt(plaintext, key, iv, key_as_bytes, padding)
    assert m2_decrypt(ciphertext, key, iv, key_as_bytes, padding) == plaintext
    return ciphertext

if EVP:
    def test(*args):
        py_ciphertext = test_pycrypto(*args)
        m2_ciphertext = test_m2crypto(*args)
        assert py_ciphertext == m2_ciphertext
else:
    test = test_pycrypto

def gen_test_inputs():
    from os import urandom
    from itertools import product

    keys = [urandom(32) for _ in xrange(2)]
    ivs = [urandom(16) for _ in xrange(2)]
    key_as_bytes = [False, True]

    # padding=False
    plaintexts = [urandom(16 * n) for n in xrange(1025)]
    for combo in product(plaintexts, keys, ivs, key_as_bytes, [False]):
        yield combo

    # padding=True
    plaintexts = [urandom(n) for n in xrange(1025)]
    for combo in product(plaintexts, keys, ivs, key_as_bytes, [True]):
        yield combo

def benchmark(test_func):
    from time import time
    t = time()
    for combo in gen_test_inputs():
        test_func(*combo)
    return time() - t

if __name__ == "__main__":
    for combo in gen_test_inputs():
        test(*combo)

    print "pycrypto: %.2fs" % benchmark(test_pycrypto)
    if EVP:
        print "M2Crypto: %.2fs" % benchmark(test_m2crypto)
