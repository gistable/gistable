# !/usr/bin/env python
# -*- coding: utf-8 -*-

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
from Crypto.Cipher import AES

aes_obj_enc = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
ret = aes_obj_enc.encrypt('11111111111111xd')

aes_obj_dec = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
print aes_obj_dec.decrypt(ret)

#  加密解密所用对象不能为同一个
# 1. 先使用openssl生成公私钥对
# openssl genrsa -out privkey.pem 2048
# 2. 将上一步生成的RSA私钥转换成PKCS#8编码，作为最终使用的私钥。
# openssl pkcs8 -topk8 -in rsa_private_key_2048.pem -out pkcs8_rsa_private_key_2048.pem -nocrypt
# 3. 导出RSA公钥，以X509编码，作为最终交换的公钥。
# openssl rsa -in rsa_private_key_2048.pem -out rsa_public_key_2048.pem -pubout
# RSA不适合用于长段文本加解密(pycrypto限制256字符)，一般用来传输密钥，之后通过密钥通过对称加密传输内容
with open('/Users/Ficapy/CodeSpace/Dev/xxx/cert/rsa_public_key_2048.pem', 'r') as f:
    pub = f.read()

with open('/Users/Ficapy/CodeSpace/Dev/xxx/cert/pkcs8_rsa_private_key_2048.pem', 'r') as f:
    pri = f.read()


# !!! 注释掉2行是为了和java平台兼容
def encrypt(pub, message):
    # RSA/ECB/PKCS1Padding
    # 128字节搞一次
    ret = ''
    input_text = message[:128]
    while input_text:
        # h = SHA.new(input_text)
        key = RSA.importKey(pub)
        cipher = PKCS1_v1_5.new(key)
        # ret += cipher.encrypt(input_text + h.digest())
        ret += cipher.encrypt(input_text)
        message = message[128:]
        input_text = message[:128]
    return ret


def decrypt(pri, ciphertext):
    key = RSA.importKey(pri)
    dsize = SHA.digest_size
    input_text = ciphertext[:256]
    ret = ''
    while input_text:
        sentinel = Random.new().read(15 + dsize)
        cipher = PKCS1_v1_5.new(key)
        _message = cipher.decrypt(input_text, sentinel)
        # ret += _message[:-dsize]
        ret += _message
        ciphertext = ciphertext[256:]
        input_text = ciphertext[:256]
    return ret


msg = decrypt(pri, encrypt(pub, 'abcd' * 128))
print len(msg)
print msg
#  以下RSA加密解密做法官方不推荐使用(至于为什么不安全我也不造)
key = RSA.importKey(pub).encrypt('xxxx', 'x')  # 第二个参数没有用处  只是为了兼容性
print RSA.importKey(pri).decrypt(key)