class PBEWithMD5AndDES(object):
    """PBES1 implementation according to RFC 2898 section 6.1"""
    SALT = '\x0c\x9d\x4a\xe4\x1e\x83\x15\xfc'
    COUNT = 5

    def __init__(self, key):
        key = self._generate_key(key, self.SALT, self.COUNT, 16)
        self.key = key[:8]
        self.iv = key[8:16]

    def encrypt(self, plaintext):
        padding = 8 - len(plaintext) % 8
        plaintext += chr(padding)*padding
        return self._cipher().encrypt(plaintext)

    def decrypt(self, ciphertext):
        plaintext = self._cipher().decrypt(ciphertext)
        return plaintext[:-ord(plaintext[-1])]

    def _cipher(self):
        return DES.new(self.key, DES.MODE_CBC, self.iv)

    def _generate_key(self, key, salt, count, length):
        key = key + salt
        for i in range(count):
            key = md5(key).digest()
        return key[:length]