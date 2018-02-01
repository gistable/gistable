import base64
try:
    from hashlib import sha1
except ImportError:
    from sha1 import new as sha1
import random
import struct
import Crypto.Cipher.DES3 as DES3

def decrypt_password(data):
    """Given the hexdump of an obfuscated password, this function will return
       the real password"""

    # Decode incoming string, it's a hexdump of a bytestring
    data = base64.b16decode(data)

    # Length check
    if len(data) < 48:
        raise ValueError("Invalid encoded data, too short")

    # The stored data consists of three parts
    key = data[:20]
    sha = data[20:40]
    password = data[40:]

    # Check whether the sha1 is correct
    if sha != sha1(password).digest():
        raise RuntimeError("Invalid encoded data, sha1 mismatch")

    # The IV is the first 8 bytes of the non-mangled key
    iv = key[:8]

    # Construct the real, obfuscated, key
    p1 = key[:19] + struct.pack('B',1 + struct.unpack('B', key[19])[0])
    p2 = key[:19] + struct.pack('B',3 + struct.unpack('B', key[19])[0])
    key_ = sha1(p1).digest() + sha1(p2).digest()[:4]

    # Encryption is 3DES, CBC
    decrypted = DES3.new(key_, DES3.MODE_CBC, iv).decrypt(password)

    # Remove padding
    padlen = struct.unpack('B', decrypted[-1])[0]
    decrypted = decrypted[:-padlen]

    return decrypted

def encrypt_password(password, key=None):
    """This function encrypts and obfuscates the given password for use in
       Cisco VPN .pcf files. The key will be randomly generated if not given"""

    # Pad password for 3DES+CBC
    padlen = 8 - (len(password) % 8)
    password += padlen * struct.pack('B', padlen)

    # Create 20-byte random key, if needed
    if not key:
        key = sha1(str(random.getrandbits(8*20))).digest()
    elif not isinstance(key, str) or len(key) != 20:
        raise ValueError("Invalid key")

    # The IV is the first 8 bytes of the key
    iv = key[:8]

    # Construct the real, obfuscated, key
    p1 = key[:19] + struct.pack('B',1 + struct.unpack('B', key[19])[0])
    p2 = key[:19] + struct.pack('B',3 + struct.unpack('B', key[19])[0])
    key_ = sha1(p1).digest() + sha1(p2).digest()[:4]

    # Encryprion is 3DES, CBC
    encrypted = DES3.new(key_, DES3.MODE_CBC, iv).encrypt(password)

    # Hexdump
    data = key + sha1(encrypted).digest() + encrypted
    return base64.b16encode(data)

if __name__ == "__main__":
    import optparse
    import sys
    usage = "\n%prog -d <password>\n%prog -e <password> [key]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', '--decrypt', dest="do_decrypt",
            action="store_true", default=False, help="Decrypt a password")
    parser.add_option('-e', '--encrypt', dest="do_encrypt",
            action="store_true", default=False, help="Encrypt a password")

    options, args = parser.parse_args()
    if not (options.do_decrypt ^ options.do_encrypt):
        parser.print_help()
        sys.exit(1)

    if (options.do_decrypt and len(args) != 1) or \
       (options.do_encrypt and len(args) not in (1,2)):
        parser.print_help()
        sys.exit(1)

    try:
        if options.do_decrypt:
            print decrypt_password(args[0])
        elif options.do_encrypt:
            print encrypt_password(*args)
    except Exception, e:
        print str(e)
        sys.exit(1)
