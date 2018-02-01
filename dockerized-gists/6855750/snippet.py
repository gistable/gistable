# Based on http://cr.yp.to/streamciphers/timings/estreambench/submissions/salsa20/chacha8/ref/chacha.c

import binascii
import numpy as np

np.seterr(over='ignore')

def rotl32(v, c):
    assert isinstance(v, np.uint32)
    assert isinstance(c, np.uint32)
    return ((v << c) | (v >> (np.uint32(32) - c)))

rotate = rotl32

def quarter_round(x, a, b, c, d):
    x[a] += x[b]; x[d] = rotate(x[d] ^ x[a], np.uint32(16))
    x[c] += x[d]; x[b] = rotate(x[b] ^ x[c], np.uint32(12))
    x[a] += x[b]; x[d] = rotate(x[d] ^ x[a], np.uint32(8))
    x[c] += x[d]; x[b] = rotate(x[b] ^ x[c], np.uint32(7))

def salsa20_wordtobyte(inp):
    x = np.copy(inp)

    i = 20
    while i > 0:
        quarter_round(x, 0, 4,  8, 12)
        quarter_round(x, 1, 5,  9, 13)
        quarter_round(x, 2, 6, 10, 14)
        quarter_round(x, 3, 7, 11, 15)
        quarter_round(x, 0, 5, 10, 15)
        quarter_round(x, 1, 6, 11, 12)
        quarter_round(x, 2, 7,  8, 13)
        quarter_round(x, 3, 4,  9, 14)
        i -= 2

    for i in range(16):
        x[i] += inp[i]

    return x.view(np.uint8)

sigma = "expand 32-byte k"

def keysetup(iv, key, position=np.uint32(0)):
    assert isinstance(position, np.uint32)
    key_arr = np.fromstring(key, np.uint32)
    iv_arr = np.fromstring(iv, np.uint32)
    const_arr = np.fromstring(sigma, np.uint32)

    ctx = np.zeros(16, np.uint32)

    ctx[4] = key_arr[0]
    ctx[5] = key_arr[1]
    ctx[6] = key_arr[2]
    ctx[7] = key_arr[3]
    ctx[8] = key_arr[4]
    ctx[9] = key_arr[5]
    ctx[10] = key_arr[6]
    ctx[11] = key_arr[7]

    ctx[0] = const_arr[0]
    ctx[1] = const_arr[1]
    ctx[2] = const_arr[2]
    ctx[3] = const_arr[3]

    ctx[12] = position
    ctx[13] = position

    ctx[14] = iv_arr[0]
    ctx[15] = iv_arr[1]

    return ctx

def encrypt_bytes(ctx, m, byts):
    c = np.zeros(len(m), np.uint8)

    if byts == np.uint32(0):
        return

    c_pos = np.uint32(0)
    m_pos = np.uint32(0)

    while True:
        output = salsa20_wordtobyte(ctx)
        ctx[12] += 1

        if ctx[12] == np.uint32(0):
            ctx[13] += 1

        if byts <= np.uint32(64):
            for i in range(byts):
                c[i + c_pos] = m[i + m_pos] ^ output[i]
            return c

        for i in range(np.uint32(64)):
            c[i + c_pos] = m[i + m_pos] ^ output[i]

        byts -= np.uint32(64)
        c_pos += np.uint32(64)
        m_pos += np.uint32(64)

def decrypt_bytes(ctx, c, byts):
    return encrypt_bytes(ctx, c, byts)

def to_string(c):
    c_str = ""
    for i in c:
        c_str += chr(i)
    return c_str

test_vectors_key = [
    "00000000000000000000000000000000000000000000000000000000"
    "00000000",
    "00000000000000000000000000000000000000000000000000000000"
    "00000001",
    "00000000000000000000000000000000000000000000000000000000"
    "00000000",
    "00000000000000000000000000000000000000000000000000000000"
    "00000000",
    "000102030405060708090a0b0c0d0e0f101112131415161718191a1b"
    "1c1d1e1f"
]

test_vectors_iv = [
    "0000000000000000",
    "0000000000000000",
    "0000000000000001",
    "0100000000000000",
    "0001020304050607"
]

test_vectors_c_expected = [
    "76b8e0ada0f13d90405d6ae55386bd28bdd219b8a08ded1aa836efcc"
    "8b770dc7da41597c5157488d7724e03fb8d84a376a43b8f41518a11c"
    "c387b669",
    "4540f05a9f1fb296d7736e7b208e3c96eb4fe1834688d2604f450952"
    "ed432d41bbe2a0b6ea7566d2a5d1e7e20d42af2c53d792b1c43fea81"
    "7e9ad275",
    "de9cba7bf3d69ef5e786dc63973f653a0b49e015adbff7134fcb7df1"
    "37821031e85a050278a7084527214f73efc7fa5b5277062eb7a0433e"
    "445f41e3",
    "ef3fdfd6c61578fbf5cf35bd3dd33b8009631634d21e42ac33960bd1"
    "38e50d32111e4caf237ee53ca8ad6426194a88545ddc497a0b466e7d"
    "6bbdb004",
    "f798a189f195e66982105ffb640bb7757f579da31602fc93ec01ac56"
    "f85ac3c134a4547b733b46413042c9440049176905d3be59ea1c53f1"
    "5916155c2be8241a38008b9a26bc35941e2444177c8ade6689de9526"
    "4986d95889fb60e84629c9bd9a5acb1cc118be563eb9b3a4a472f82e"
    "09a7e778492b562ef7130e88dfe031c79db9d4f7c7a899151b9a4750"
    "32b63fc385245fe054e3dd5a97a5f576fe064025d3ce042c566ab2c5"
    "07b138db853e3d6959660996546cc9c4a6eafdc777c040d70eaf46f7"
    "6dad3979e5c5360c3317166a1c894c94a371876a94df7628fe4eaaf2"
    "ccb27d5aaae0ad7ad0f9d4b6ad3b54098746d4524d38407a6deb"
]

def test_passes(i):
    key = binascii.unhexlify(test_vectors_key[i])
    iv = binascii.unhexlify(test_vectors_iv[i])
    c_expected = test_vectors_c_expected[i]

    m = np.zeros(len(c_expected) / 2, np.uint8)

    ctx = keysetup(iv, key)
    c = encrypt_bytes(ctx, m, len(m))
    c_str = to_string(c)
    return binascii.hexlify(c_str) == c_expected

def run_tests():
    amount_tests = len(test_vectors_c_expected)

    for i in range(amount_tests):
        print "{0}. TEST RESULT: {1}".format(i, test_passes(i))

if __name__ == "__main__":
    run_tests()
