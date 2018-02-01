#!/usr/bin/env python
from __future__ import print_function


import base64
import sys


PEM = ("""-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAgK1Q6Ydi8UUheJLvnTYJE65NOZtAtjDdDSxS+6b4x9EakjIylljSzs5uLEJn
kCe4f/vvQKrAKQiQdcjTM8Ea/wiS/Mj+xSGD3Sfk0BuRuYat9gpwCFY9mzyruesp6WAE5hXmsDNQ
I1sY3b2xJePnP4YWV+2oUaXn11vpOOTk7XVwnP7VfQu8PIIRHVJbZfV2C6rkCIhJrzBfa3jIe6F/
KY+dTwu5CZHiopuPsjbbSKfqhLf4f3zUBcdgUsdZCB21LoBNWvGpPZlQJ1VvXWHkwYNo1r5L35H0
7KarS8Y6D3gL29YKvtkY/UHvyuNDcwM02IUewdrHDaGiOEiUsarmyQIDAQABAoH/VPIVeBToPF5m
ujJF/IKve06VrHHRRnT7eLbKEVco5MAlyl1ZB+ebQusD0DQGKiQOqG6ogwg10uDUfO0WgBP6vmHq
pvYJOhnl8xli8/8/NDq0nLhHPTmxccmblCCqimXY1gufPrKhNLXutHOFfn31KvpZxbIea8gaRRFn
5Sc1+YueD4Bq6P/XRnQjAvAGmMTuNMbvHwX8K6JKNh6JNpPkJQ5+dXpd16ahAwYMsWaCLjTikoOb
NEhviVz22rJMw/KWCQYyIWHDaQd7QMhXdP2BUwbans7U1d+Igw6/dXf9BufM5d2IB02idTB/jFRE
6QtCb3kmBVBZdEwmPCUkqHRlAoGBALrmZGMxcY94rd922/H94hPmUlJPG1fxG+lnMAALdC7tpC73
dmlEYDdsEQW5Y9C9wSraIawxd0xtxOG90ZbZ/yMqpFZ9+5FVr3zpGrMxngDV92KLrJ2AElD/CeLB
NatNJoO+mqKuW6vX3XEZA2KqX3oTm0zhhS5nazZixmt1dAYbAoGBALBAROTLulzSh9SLFWiY3A1a
zoK7ATusesUFLeY6/K6SV4dQDT6fTDiZh2qXMir88UDCOBxCEjGGIw+sMh3iAUHBzHdi5xtAFesN
WyjfhddTQwtfRgO93P+/RgvssrhsItWqnTfAdNkO7+woSjC0eQ7fEdWsIYhWdqSW9LZowKTrAoGB
AIbUGettCc1Ec7pXlofWbTeJ2i1CoCkq6MXSCNCfcqtACEdRgfyitP6GWSlV+mnl2eo9/jioXrWm
InfvZbl7fhEye+dhbxADTlvAFeDblG5p7NMMi/P7JjuEIO+SDlOLjpNP92IQglVPnpIuR0DwQ3xf
lJM7xcYaGT/cteNjkdWtAoGBAKk5S+yRXyH4UcpUr/15pu57nYQPoSN2e3nneyZuxGWoxLl6tvzF
Xh2J62cAPH7h1ZFj6RPYrDc4nzlRD915PdOxC2wlXdfgNCs266vW0V7o5ppoo4S8KxCyycJxRTel
O90Cr2j0NDykBuAr3u/cl88bhrgtSRTqT4fAGL163lx5AoGAWiWgczL19PAIzv2WxnRmlwIexPBG
6A+KURg4/APfZOxa5rA91lKU2cQoGqgHErWhSdfZrdyNSqppAFtdB8Sgy1irkKGLBBiWOq4hfX2V
pCGks4zzBYQJ27/GnY2gbv6U6bBx2JW2zDvZZSU6ckv6eoJ2YEVMn63uzdpdwXlsTzE=
-----END RSA PRIVATE KEY-----""")


def via_cryptography(message):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    private_key = serialization.load_pem_private_key(
	PEM, password=None, backend=default_backend())
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


def via_openssl(message):
    import subprocess
    import tempfile
    with open("my-pem", "wb+") as f:
        f.write(PEM)
        f.flush()
	p = subprocess.Popen(
            "openssl rsautl -sign -inkey " + f.name,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input=message)
    if stderr or p.returncode != 0:
        print(stderr)
    return stdout


def via_pycrypto(message):
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA
    from Crypto.Signature import PKCS1_PSS
    rsakey = RSA.importKey(PEM)
    return rsakey.encrypt(message, None)[0]


def via_pyopenssl(message, digest="sha1"):
    import OpenSSL
    key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, PEM)
    return OpenSSL.crypto.sign(key, message, digest)


def via_rsa(message):
    import rsa
    privkey = rsa.PrivateKey.load_pkcs1(PEM)
    return rsa.sign(message, privkey, "SHA-1")


def via_ruby(message):
    import subprocess
    syntax = (
        "require 'openssl'; key = OpenSSL::PKey::RSA.new('%s'); "
        "print key.private_encrypt('asdf')"
    ) % PEM
    return subprocess.check_output('ruby -e "%s"' % syntax, shell=True)


if __name__ == "__main__":
    message = "asdf"
    for each in (via_cryptography, via_openssl, via_pycrypto, via_pyopenssl,
                 via_rsa, via_ruby):
        print("Using %s:" % each.__name__)
        print(base64.b64encode(each(message)))
        print()