import binascii
import itertools


def xor_strings(a, b):
    return ''.join(
        [chr(ord(x) ^ ord(y)) for x, y in zip(a, itertools.cycle(b))])


def xor_hex_strings(a, b):
    return ''.join(
        ['{:x}'.format(int(x, 16) ^ int(y, 16)) for x, y in zip(a, b)])


def encrypt(text, key):
    cipher = xor_strings(text, key)
    return (binascii.hexlify(cipher.encode())).decode()


def decrypt(cipher, key):
    cipher = (binascii.unhexlify(cipher.encode())).decode()
    return xor_strings(cipher, key)


def two_time_pad_attack(cipher1, cipher2):
    # ascii_table = [
    #     ['CtrChar'] * 32,
    #     list(" !\"#$%&'()*+,-./ 0123456789:;<=>?"),
    #     list("@ABCDEFGHIJKLMNO PQRSTUVWXYZ[\]^_"),
    #     list("`abcdefghijklmno pqrstuvwxyz{|}~.")
    # ]

    # xored_messages = xor_hex_strings(cipher1, cipher2)
    # recovered = ""
    # return recovered
    pass
