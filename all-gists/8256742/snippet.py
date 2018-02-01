import sys
import subprocess
import io

class PacketReader(object):

    packetTagNames = {
        0: 'Reserved - a packet tag MUST NOT have this value',
        1: 'Public-Key Encrypted Session Key Packet',
        2: 'Signature Packet',
        3: 'Symmetric-Key Encrypted Session Key Packet',
        4: 'One-Pass Signature Packet',
        5: 'Secret-Key Packet',
        6: 'Public-Key Packet',
        7: 'Secret-Subkey Packet',
        8: 'Compressed Data Packet',
        9: 'Symmetrically Encrypted Data Packet',
        10: 'Marker Packet',
        11: 'Literal Data Packet',
        12: 'Trust Packet',
        13: 'User ID Packet',
        14: 'Public-Subkey Packet',
        17: 'User Attribute Packet',
        18: 'Sym. Encrypted and Integrity Protected Data Packet',
        19: 'Modification Detection Code Packet',
    }

    publicKeyAlgos = {
        1: ('RSA (Encrypt or Sign)', ['n', 'e']),
        2: ('RSA Encrypt-Only', ['n', 'e']),
        3: ('RSA Sign-Only', ['n', 'e']),
        16: ('Elgamal (Encrypt-Only)', ['p', 'g', 'y']),
        17: ('DSA (Digital Signature Algorithm)', ['p', 'q', 'g', 'y']),
        18: ('Reserved for Elliptic Curve', None),
        19: ('Reserved for ECDSA', None),
        20: ('Reserved (formerly Elgamal Encrypt or Sign)', None),
        21: ('Reserved for Diffie-Hellman (X9.42, as defined for IETF-S/MIME)',
             None)
    }

    wrapWidth = 79

    def __init__(self, strm, indent=''):
        self.strm = strm
        self.indent = indent
        while self.readPacket(True):
            pass

    def print(self, msg):
        print(self.indent + msg)

    def wrapped(self, label, text):
        w = self.wrapWidth - len(label) - len(self.indent)
        w -= w & 1
        lns = []
        while len(text) > w:
            lns.append(text[-w:])
            text = text[:-w]
        self.print(label + ' '*(w - len(text)) + text)
        pad = ' '*len(label)
        for l in reversed(lns):
            self.print(pad + l)

    def readPacket(self, mayBeAtEOF=False):
        ptag = self.strm.read(1)
        if len(ptag) == 0:
            if mayBeAtEOF:
                return False
            raise Exception("More packets expected")
        ptag = ptag[0]
        if (ptag & 0x80) == 0:
            raise Exception("Invalid Packet Header")
        plen = 0
        if ptag & 0x40:
            # new format
            raise Exception("Don't handle new format")
        else:
            # old format
            lt = ptag & 0x03
            tag = (ptag & 0x3c) >> 2
            if lt == 3:
                raise Exception("Don't handle indeterminate length")
            for i in range((1, 2, 4)[lt]):
                plen = 0x100*plen + self.byte()
        pdata = self.read(plen)
        self.print("Packet {:2} length {:5} -- {}"
                   .format(tag, plen,
                           self.packetTagNames.get(tag, '(unknown)')))
        mtd = getattr(self, "pkg{}".format(tag), None)
        if mtd is None:
            self.print("  (skipping)")
        else:
            strm = self.strm
            indent = self.indent
            self.indent = '  ' + indent
            self.strm = io.BytesIO(pdata)
            try:
                mtd(pdata)
            finally:
                self.indent = indent
                self.strm = strm
        return True

    def read(self, n):
        d = self.strm.read(n)
        if len(d) != n:
            raise Exception("Premature end of data")
        return d

    def byte(self):
        return self.read(1)[0]

    def expectEOF(self):
        if len(self.strm.read(1)) != 0:
            raise Exception("Expected end of stream")

    def dbl(self):
        a, b = self.read(2)
        return (a << 8) | b

    def quad(self):
        a, b, c, d = self.read(4)
        return (a << 24) | (b << 16) | (c << 8) | d

    def mpi(self):
        l = self.dbl()
        b = self.read((l + 7)//8)
        h = ''.join("{:02x}".format(i) for i in b)
        d = 0
        for i in b:
            d = 0x100*d + i
        return (l, b, h, d)

    def pkg6(self, pdata):
        """Read public key packet"""
        ver = self.byte()
        if ver != 4:
            raise Exception("Key version {} unsupported".format(ver))
        self.print("time = {}".format(self.quad()))
        algo = self.byte()
        name, elts = self.publicKeyAlgos.get(algo, ('(unknown)', None))
        self.print("algo = {} -- {}".format(algo, name))
        if elts is None:
            self.print("(don't know how to hanle this algo)")
            return
        for elt in elts:
            l, b, h, d = self.mpi()
            self.print(elt)
            self.print("  len = {}".format(l))
            self.wrapped("  hex = ", h)
            self.wrapped("  int = ", str(d))
        self.expectEOF()

for id in sys.argv[1:]:
    data = subprocess.check_output(["gpg", "--export", id])
    PacketReader(io.BytesIO(data))
