import binascii
from Crypto.Cipher import AES
from Crypto.Random.random import getrandbits
from hashlib import md5
from schematics.types import StringType
import struct


class DecryptionException(Exception):
    pass


class Encryptor(object):
    '''
    A class which encapsulates the logic for encrypting and decrypting
    strings using the algorithm and protocol we want to use
    (aes-256-cbc). It takes two arguments when created -- the password
    to use, and the magic "number" (actually a string) to prepend to
    encrypted string if any -- and has three public methods --
    decrypt(), encrypt(), and set_password().

    decrypt() takes the encrypted, base64-encoded database field and
    returns the decrypted string.

    decrypt() has the following special behavior -- if the string
    passed into it isn't valid base64, or if the decoded string
    doesn't start with "Salted__", it assumes that the string is
    already decrypted and returns it as-is.

    encrypt() takes a plaintext string and returns an encrypted,
    base64-encoded string to be stored in the database.

    set_password() takes a new password and replaces the previous
    password with the new one.
    '''

    def __init__(self, password, magic_number=''):
        # It would be nice if we could convert the password into a key
        # and then forget it, but we can't do that, because each time
        # we decrypt there will be a different salt and therefore a
        # different key and IV.
        self.password = password
        self.magic_number = magic_number

    def decrypt(self, base64_string):
        if not isinstance(base64_string, (str, unicode)):
            return base64_string
        if self.magic_number:
            if base64_string[0:len(self.magic_number)] != self.magic_number:
                # Not encrypted?
                return base64_string
            base64_string = base64_string[len(self.magic_number):]
        try:
            binary_string = binascii.a2b_base64(base64_string)
        except:
            # Must already be decrypted.
            return base64_string
        if binary_string[0:8] != 'Salted__':
            # Not encrypted the way we expect, so punt on decryption.
            return base64_string

        # The salt is the 9th through 16th bytes in the encrypted
        # string.
        salt = binary_string[8:16]

        # The key is produced from the password and salt. The 32-bit
        # key length is required for 256-bit AES, and the 16-byte IV
        # length is required for AES CBC.
        key, iv = self.EVP_ByteToKey(self.password, salt, 32, 16)

        # The data is everything after the 16th byte in the encrypted
        # string.
        data = binary_string[16:]

        encryptor = AES.new(key, AES.MODE_CBC, iv)
        decrypted = self.unpad(encryptor.decrypt(data))
        try:
            return decrypted.decode('utf-8')
        except UnicodeDecodeError:
            # This means the decrypted string is garbage, so wrong password,
            # probably.
            raise DecryptionException('Decryption failure; bad password?')

    def encrypt(self, plaintext):
        plaintext = self.pad(plaintext.encode('utf-8'))
        salt = self.random_salt()
        key, iv = self.EVP_ByteToKey(self.password, salt, 32, 16)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        binary_string = 'Salted__' + salt + encryptor.encrypt(plaintext)
        base64_string = self.magic_number + binascii.b2a_base64(binary_string)
        return base64_string

    def set_password(self, password):
        self.password = password

    def random_salt(self):
        return struct.pack('=Q', getrandbits(64))

    # AES CBC requires blocks to be aligned on 16-byte boundaries.
    BS = 16

    # PKCS#7 pad and unpad routines.

    def pad(self, s):
        return s + (self.BS - len(s) % self.BS) * \
            chr(self.BS - len(s) % self.BS)

    @staticmethod
    def unpad(s):
        return s[0:-ord(s[-1])]

    # This is the algorithm that openssl uses to turn a password and
    # salt into an encryption key and IV. Since the
    # mongoid-encrypted-fields Gem we're using on the Ruby side does
    # openssl-compatible encryption, we need to as well, so we need to
    # use the same algorithm that it and OpenSSL use.

    @staticmethod
    def EVP_ByteToKey(password, salt, key_len, iv_len):
        """
        Derive the key and the IV from the given password and salt.
        """
        dtot = md5(password + salt).digest()
        d = [dtot]
        while len(dtot) < (iv_len + key_len):
            d.append(md5(d[-1] + password + salt).digest())
            dtot += d[-1]
        return dtot[:key_len], dtot[key_len:key_len + iv_len]


def MakeSchematicsEncryptedType(schematics_type, encryptor):
    '''
    Returns an encrypted version of a scalar Schematics type.

    Don't try to double-encrypt fields, i.e., to store an
    encrypted string as a field value. That will yield unpredictable
    results.
    '''

    if not issubclass(schematics_type, StringType):
        raise Exception('This code has only been tested with strings.')

    class EncryptedType(schematics_type):
        options = {'nested_for_python': None,
                   'nested_for_json': None}

        def __set__(self, instance, value):
            super(EncryptedType, self).__set__(instance,
                                               encryptor.decrypt(value))

        def for_python(self, value):
            # We need to protect against a type implementation wher
            # for_python calls for_json or vice versa.
            val = unicode(super(EncryptedType, self).for_python(value))
            if self.options['nested_for_python'] is None:
                try:
                    dec = encryptor.decrypt(val)
                    if dec == val:
                        raise Exception('Fall through to except')
                    else:
                        self.options['nested_for_python'] = True
                        return val
                except:
                    self.options['nested_for_python'] = False
                    return encryptor.encrypt(val)

            elif self.options['nested_for_python']:
                return val
            else:
                return encryptor.encrypt(val)

        def for_json(self, value):
            # We need to protect against a type implementation wher
            # for_python calls for_json or vice versa.
            val = unicode(super(EncryptedType, self).for_json(value))
            if self.options['nested_for_json'] is None:
                try:
                    dec = encryptor.decrypt(val)
                    if dec == val:
                        raise Exception('Fall through to except:')
                    else:
                        self.options['nested_for_json'] = True
                        return val
                except:
                    self.options['nested_for_json'] = False
                    return encryptor.encrypt(val)
            elif self.options['nested_for_json']:
                return val
            else:
                return encryptor.encrypt(val)

    return EncryptedType
