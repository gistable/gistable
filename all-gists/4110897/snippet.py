# you need to install python-gpgme

import StringIO
import urllib
import gpgme
import shutil, tempfile
import os
from contextlib import closing, contextmanager

tarball = 'http://pypi.python.org/packages/source/s/signtest/signtest-1.0.tar.gz'
signature = 'http://pypi.python.org/packages/source/s/signtest/signtest-1.0.tar.gz.asc'


# get the tarball
tarball, headers = urllib.urlretrieve(tarball)


# get the signature file
signature, headers = urllib.urlretrieve(signature)


@contextmanager
def gpgme_context(keys):
    gpg_conf_contents = ''
    _gpghome = tempfile.mkdtemp(prefix='tmp.gpghome')

    try:
        os.environ['GNUPGHOME'] = _gpghome
        fp = open(os.path.join(_gpghome, 'gpg.conf'), 'wb')
        fp.write(gpg_conf_contents)
        fp.close()
        ctx = gpgme.Context()

        loaded = []
        for key_file in keys:
            result = ctx.import_(key_file)
            key = ctx.get_key(result.imports[0][0])
            loaded.append(key)

        ctx.signers = loaded

        yield ctx
    finally:
        del os.environ['GNUPGHOME']
        shutil.rmtree(_gpghome, ignore_errors=True)


def verify(pubkey, tarball, signature):

    with open(signature) as f:
        signature = StringIO.StringIO(f.read())

    with open(tarball) as f:
        tarball = StringIO.StringIO(f.read())


    with gpgme_context([pubkey]) as ctx:
        sigs = ctx.verify(signature, tarball, None)
        return sigs[0].status == None



KEY = '''\
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.12 (Darwin)

mQENBFCqOm4BCAC5l7jmbELOG0VzcDukoAztGvhNe37ziIz/c0zi64TppcK4M9hP
uO9wRgS99zLiMZ+bqfyBIrkpltcSknP0J+RiUSEWHKI+MExwDYhIrkmjxtL6Tcga
BGSZj/8rpQdy9+Hsa5OQdf/RzYGlLBVROnWGVKynD8gtknw68jKU5h9YlmMXYJdt
tXEP32lq78jcvFl1+QJFx8EtYKVeVwLcrXfw6uB72pcYWLPxEUS/4LhjWa1RzXBR
M4Y/vBRYYF2yEjs9IGbvZylOtxIoOM/Ojlf14nwnI1XSLYBQzUik8c347zxp/eVu
K4c1f8Y637aVJa325aWL63TrnCcCTPm26H8dABEBAAG0F1RhcmVrIDx0YXJla0B6
aWFkZS5vcmc+iQE4BBMBAgAiBQJQqjpuAhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIe
AQIXgAAKCRBYlYjicW0iY2k4B/4xID5/2fyIq9TcEWNVjGMpi4cgFV1qyI2r8W7C
C7e+F7LQHFWBGFYt4ldvT3LXb9gpz9HM0b1JAmdqqu0eUb612moUxG+kAWHJSa/y
sZz+FiXbQueEuQD8m8mD2txLYput45GRRMqQr/lRUQfEN3jmqOauFIXvMZ4Y8YUh
3I1z3StNxc+vIgshBKSXdtEiYpGeL9RfvmESgaWGYQgyp4F8QKIh0oFBvKU+xMF4
QO7e7IyMp3KeYQKatTtTYP1K/kpBr9e4XO1SKix27sWRx595BgMqIjRsXI7RAaSu
rHpfgSxONT26RS/v04T+mP29L8Z2qu25ghCCFPyZwZ2OA7qluQENBFCqOm4BCADh
gFrB4/sAH4uHLmV/0hrnRejqCZbNpTtPm8wZhfbC/5qQuKQdPP8oPwtHMFNSs4vF
ndblZadfzLZoCCzH1DX6uoDcBIJmjVP8qS50yklwaCYy7mBCvTRsycv6zxCaNFVK
9v9X6/8xaMYq3DQFrjpr3JfzzJXr1v2tnuae4BvoqRhL5I7yj3gG/yBVQLg8LAGx
5snfq7eHjrecN0G/o9k+bSn8OHMUVcN9s4SZZuZZe8Ote+dAOoK2Z6W/BYIv79bk
q/WDwjHHN3eXZzC7R+LenCb6OAXTeOWYkjXvkbw6OVsK7LymWqMaN6zycj4hTLu7
tiAhtGO1pejpxVHH+eO3ABEBAAGJAR8EGAECAAkFAlCqOm4CGwwACgkQWJWI4nFt
ImOBMQgAl100U/U8x7wfpmZ+nIzyvwBm8wjk8Q5RWqDHA5ja/TuxXzmyuxX3m773
6TK8Ve6k1/IUPubk+r3hLzE2ejFMJU92LIv1MCFhgn8mIpocmOWtyv7oXVm82i9v
QXkuS2SbXXgdFvq7SVfWpC9nNsP1axPk0uuY5AdLqNkmoaJ3Z0ARPLebzjD5mMDJ
xySdyD8cHCZt9nmsk3CTxkqiQokw/THRqUkxsP4hd58heVMKTJFkPCWjUvJmB+uh
ywRDETQxSkbQUnFen7g5ylAzlZSKo04I6yXourBdtiwPs63Ufnn0yV1T7Sv5SwMq
RKWV6KCLCry/RcOVeRtzrBB+ddxb8Q==
=Nlrz
-----END PGP PUBLIC KEY BLOCK-----'''


try:
    if not verify(StringIO.StringIO(KEY), tarball, signature):
        print 'BAD signature'
    else:
        print 'OK'
finally:
    os.remove(tarball)
    os.remove(signature)