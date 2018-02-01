'''
Implementations of some basic elliptic curve cryptography primitivese.

Behavior specified by SECG in SEC1 version 1 and 2.
Also ANSI X9.63.

Curves specified from SEC2 version 1 and 2,
and NIST "Recommended Elliptic Curves for Federal Government Use".

See: http://en.wikipedia.org/wiki/Elliptic_curve_cryptography and
http://www.johannes-bauer.com/compsci/ecc/?menuid=4 and
http://www.dkrypt.com/home/ecc
for mathematical background.
'''
import collections, random, binascii
import hashlib, hmac

from Crypto.Cipher import DES3, XOR, AES
from Crypto.Util.strxor import strxor

class Point(collections.namedtuple("EC_Point", "x y curve")):
    'represents a point on a prime field, curve of the form yy = xxx + ax + b'
    def _add(self, other):
        a = self.curve.a
        prime = self.curve.p
        p = self
        q = other
        if p != q:
            s = _divmod(q.y - p.y, q.x - p.x, prime)
        else: #point doubling
            s = _divmod(3*p.x*p.x + a, 2*p.y, prime)
        x = s*s - p.x - q.x
        y = s*(p.x - x) - p.y
        return Point(x % prime, y % prime, self.curve)


    def __add__(self, other):
        if other == 0: #TODO: what is zero for an EC_Point?
            return self
        #if not isinstance(other, Point):
        #    raise ValueError("Points can not be added to "+type(other).__name__)
        if self.curve != other.curve:
            raise ValueError("only points on the same curve can be added")
        #implemented from http://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_addition
        return self._add(other)

    __radd__ = __add__

    def __rmul__(self, num):
        acc = 0 #TODO: what is zero for an EC_Point?
        doubler = self
        while num >= 1:
            if num & 1:
                acc += doubler
            num >>= 1
            doubler += doubler
        return acc

    __mul__ = __rmul__

    def check(self): #sanity check that current point is on its own curve
        lhs = self.y**2
        rhs = self.x**3 + self.curve.a * self.x + self.curve.b
        return lhs % self.curve.p == rhs % self.curve.p

    def compress(self):
        return self.x*2 + self.y

def sec_decode(curve, data):
    'octet-string decoding as defined in section 2.3.3 of SEC1'
    if data[0] == '\x04':
        raise ValueError("uncompressed format not yet supported")
    elif data[0] == '\x02':
        y_p = 0
    elif data[0] == '\x03':
        y_p = 1
    else:
        raise ValueError("invalid data: first byte must be one of 02, 03, 04")

    if isinstance(curve, Curve):
        x = int(binascii.hexlify(data[1:]), 16)
        assert x < curve.p, "encoded point is not within range of curve points"
        alpha = ( x**3 + curve.a*x + curve.b ) % curve.p
        beta = _sqrt_mod(alpha, curve.p)
        if beta % 2 == y_p:
            y = beta
        else:
            y = curve.p - beta
        point =  Point(x,y,curve)
    elif isinstance(curve, BinaryFieldCurve):
        x = _BinaryFieldInt(binascii.hexlify(data[1:]), 16)
        #assert x < 2**(int(math.log(curve.f, 2))+1), "encoded point is not within range of curve points"
        inv_x, _ = _extended_gcd(x, curve.f)
        beta = (x + curve.a + curve.b * inv_x*inv_x) % curve.f
        # "find an element z such that z**2 + z = beta"
        z = _quadr_solve(beta, curve.f)
        if z%2 == y_p:
            y = (x * z) % curve.f
        else:
            y = (x * (z + 1)) % curve.f
        point = BinaryPoint(x,y,curve)
    else:
        raise ValueError("unrecognized curve type")

    if not point.check():
        raise ValueError("point is not on curve")
    return point

def sec_encode(point, compressed=True):
    'octet-string encoding as defined in section 2.3.4 of SEC1'
    curve = point.curve
    #TODO: calculate length properly
    x = "{0:X}".format(point.x)
    if len(x)%2:
        x = "0"+x
    x = binascii.unhexlify(x)
    if compressed:
        if isinstance(curve, Curve):
            y = point.y
        else:
            #inverse of point y for BinaryFieldCurve
            y, _ = _extended_gcd(point.y, curve.f)
        if y & 0x1: #don't use modulus
            output = '\x03' + x
        else:
            output = '\x02' + x
        return output
    else:
        y = "{0:X}".format(point.y)
        if len(y)%2:
            y = "0"+y
        y = binascii.unhexlify(y)
        return "\x04"+x+y


class BinaryPoint(Point):
    'Represents a point on a binary field, curve of the form yy + xy = xxx + axx + b'
    def __new__(cls, x, y, curve):
        return Point.__new__(cls, _BinaryFieldInt(x), _BinaryFieldInt(y), curve)

    def _add(self, other):
        a = self.curve.a 
        b = self.curve.b
        p = self
        q = other
        f = self.curve.f
        if p == q: #point doubling
            s = p.x + _divmod(p.y, p.x, f)
            x = s*s + s + a
            y = p.x*p.x + (s+1)*x
        else:
            s = _divmod(p.y + q.y, p.x + q.x, f)
            x = s*s + s + p.x + q.x + a
            y = s*(p.x + x) + x + p.y
        return BinaryPoint(x%f, y%f, self.curve)

    def check(self):
        lhs = self.y*self.y + self.x*self.y
        rhs = self.x*self.x*self.x + self.curve.a * self.x*self.x + self.curve.b
        return lhs % self.curve.f == rhs % self.curve.f

Curve = collections.namedtuple("EllipticCurve", "a b p")
#representing the equation y**2 = x**3 + a*x + b % p

_BinaryFieldCurve = collections.namedtuple("BinaryFieldEllipticCurve", "a b f")
class BinaryFieldCurve(_BinaryFieldCurve):
    def __new__(cls, a, b, f):
        a = _BinaryFieldInt(a)
        b = _BinaryFieldInt(b)
        if type(f) is list:
            f = sum([2**e for e in f]) + 1
        f = _BinaryFieldInt(f)
        return _BinaryFieldCurve.__new__(cls,a,b,f)
#representing the equation y*y + y*x = x*x*x + a*x*x + b
#over the field of polynomials whose coefficients are {0,1}, aka GF(2)

class Encryptor(object):
    def __init__(self, curve, G, n, h):
        self.curve = curve #the particular elliptic curve
        self.G = G #a Generator EC_Point on the curve
        self.n = n #the order of the curve generator G; that is n*G % p = G
        #multiplying G by more than n is pointless -- it just loops back around
        self.h = h # the cofactor of the curve, it is the quotient of the number of curve-points

        #pre-calculate size of serialized field elements
        if isinstance(curve, Curve):
            curve_size = len("{0:x}".format(curve.p))
        else:
            curve_size = len("{0:x}".format(curve.f))
        self.curve_size = (curve_size + curve_size%2)/2

    @classmethod
    def make_curve(self, curve, G_x, G_y, n, h=None):
        G = Point(G_x, G_y, curve)
        if not G.check():
            raise ValueError("Invalid: generator point not on curve")
        return Encryptor(curve, G, n, h)

    @classmethod
    def make_binary_curve(self, curve, G_x, G_y, n, h=None):
        G = BinaryPoint(G_x, G_y, curve)
        if not G.check():
            raise ValueError("Invalid: generator point not on curve")
        return Encryptor(curve, G, n, h)

    def gen_keypair(self, private=None):
        if private is None:
            private = random.randint(1, self.n)
        public = private * self.G
        return private, public

    def encrypt(self, public, r=None):
        if r is None:
            r = random.randint(1, self.n)
        R = r * self.G #to be transmitted
        S = r * public #secret key
        #only with corresponding private key, can secret key S be recovered
        return R, S

    def decrypt(self, private, R):
        S = private * R
        return S

MODE_CERTICOM98 = "certicom98"
MODE_STANDARD = "standard"

class ECAES(object):
    '''
    Elliptic Curve Augmented Encryption Scheme,
    aka Elliptic Curve Integrated Encryption Scheme (ECIES),
    aka Elliptic Curve Encryption Scheme (ECES)
    '''

    def __init__(self, elliptic_curve_encryptor, public_key, private_key, key_hash=hashlib.sha1,
                        cipher=DES3, cipher_key_len=None, mac_hash=hashlib.sha1, compress_points=True,
                        cofactor_diffie_hellman=False, mode=MODE_STANDARD):
        self.encryptor = elliptic_curve_encryptor
        self.public_key = public_key
        self.private_key = private_key
        self.cipher = cipher
        if cipher_key_len is None:
            if cipher in (DES3, AES):
                self.cipher_key_len = 24
            else:
                self.cipher_key_len = None
        self.mac_len = len(mac_hash('test').digest())
        self.mac_hash = mac_hash
        self.key_hash = key_hash
        self.compress_points = compress_points
        self.cofactor_diffie_hellman = cofactor_diffie_hellman
        self.mode = mode #certicom or standard


    def encrypt(self, plaintext, r=None):
        if r is None:
            r = random.randint(1, self.encryptor.n)
        point = r * self.public_key
        cipher_key_len = self.cipher_key_len or len(plaintext) #for xor cipher
        mac_key_len = self.mac_len
        keys = self.derive_keys(point, cipher_key_len + mac_key_len)
        cipher_key, mac_key = keys[:cipher_key_len], keys[cipher_key_len:]
        if self.cipher is DES3:
            cipher = DES3.new(cipher_key, mode=DES3.MODE_CBC)
        elif self.cipher is AES:
            cipher = AES.new(cipher_key, mode=AES.MODE_CBC)
        elif self.cipher is XOR:
            cipher = XOR.new(cipher_key)
        ciphertext = cipher.encrypt(plaintext)
        cmp_point = sec_encode(r * self.encryptor.G, self.compress_points)
        mac = hmac.new(mac_key, ciphertext, self.mac_hash).digest()
        return cmp_point + ciphertext + mac

    def decrypt(self, data):
        curve_size = self.encryptor.curve_size
        point = data[:curve_size+1]
        if self.mode == MODE_CERTICOM98:
            mac_end = curve_size+1+self.mac_len
            mac, ciphertext = data[curve_size+1:mac_end], data[mac_end:]
        else: 
            ciphertext, mac = data[curve_size+1:-self.mac_len], data[-self.mac_len:]
        point = sec_decode(self.encryptor.curve, point)
        point = self.private_key * point
        cipher_key_len = self.cipher_key_len or len(ciphertext) #for xor cipher
        mac_key_len = self.mac_len
        keys = self.derive_keys(point, cipher_key_len + mac_key_len)
        cipher_key, mac_key = keys[:cipher_key_len], keys[cipher_key_len:]

        #cur_mac = hmac.new(mac_key, ciphertext, self.mac_hash).digest()
        #print binascii.hexlify(cur_mac).upper()
        #print binascii.hexlify(mac).upper()
        #assert mac == cur_mac, "mac mismatch"
        if self.cipher is DES3:
            cipher = DES3.new(cipher_key, mode=DES3.MODE_CBC)
        elif self.cipher is AES:
            cipher = AES.new(cipher_key, mode=AES.MODE_CBC)
        elif self.cipher is XOR:
            return strxor(cipher_key, ciphertext)
        return cipher.decrypt(ciphertext)

    def derive_keys(self, point, keylen):
        'X9.63 key derivation function'
        curve_size = self.encryptor.curve_size
        if self.cofactor_diffie_hellman:
            point = self.encryptor.h * point
        shared_secret = binascii.unhexlify("{0:0{1:d}X}".format(point.x, curve_size*2))
        #certicom does some crazy complex shared_secret derivation
        sofar = 0
        keys = []
        if self.mode == MODE_CERTICOM98:
            counter = 0
        else:
            counter = 1
        while sofar < keylen:
            count = '\0\0\0'+chr(counter)
            if self.mode == MODE_CERTICOM98:
                cur = count+shared_secret
            else:
                cur = shared_secret+count
            keys.append(self.key_hash(cur).digest())
            sofar += len(keys[-1])
            counter += 1
        return "".join(keys)[:keylen]

#division in integers modulus p means finding the inverse of the denominator
#modulo p and then multiplying the numerator by this inverse
#(Note: inverse of A is B such that A*B % p == 1)
#this can be computed via extended euclidean algorithm
# http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
def _extended_gcd(a, b):
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a / b
        a, b = b,  a%b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

#TODO: optimize: a/b and a%b are the same operation underneath for _BinaryFieldInts
#this is the dominating operation performance wise, so reducing this will be 2x speedup

def _divmod(num, den, p):
    inv, _ = _extended_gcd(den, p)
    return num * inv

def jacobi(a, n):
    t = 1
    while a != 0:
        while a % 2 == 0:
            a >>= 1
            if n % 8 == 3 or n % 8 == 5: t = -t
        if a < n:
            a, n = n, a
            if a % 4 == 3 and n % 4 == 3: t = -t
        a = (a - n) >> 1
        if n % 8 == 3 or n % 8 == 5: t = -t
    if n == 1: return t
    else: return 0

#http://en.wikipedia.org/wiki/Shanks%E2%80%93Tonelli_algorithm
#http://codereview.stackexchange.com/questions/14982/tonelli-shanks-algorithm-in-python
def _sqrt_mod(a, p):
    'Tonelli-Shanks algorithm, p must be a prime number'
    a = a % p
    if p % 8 == 3 or p % 8 == 7:
        return pow(a, (p+1)/4, p)
    elif p % 8 == 5:
        x = pow(a, (p+3)/8, p)
        c = (x*x) % p
        if a == c:
            return x
        return (x * pow(2, (p-1)/4, p)) % p
    else:
        # find a quadratic non-residue d
        d = 2
        while jacobi(d, p) > -1:
            d += 1
        # set p-1 = 2^s * t with t odd
        t = p - 1
        s = 0
        while t % 2 == 0:
            t /= 2
            s += 1
        at = pow(a, t, p)
        dt = pow(d, t, p)
        m = 0
        for i in xrange(0, s):
            if pow(at * pow(dt, m), pow(2, s-1-i), p) == (p-1):
                m = m + pow(2, i)
        return (pow(a, (t+1)/2) * pow(dt, m/2)) % p

class _BinaryFieldInt(long):
    def __add__(self, o): return _BinaryFieldInt(self ^ o)
    __radd__ = __add__
    __sub__  = __add__
    __rsub__ = __add__
    def __mul__(self, o): 
        acc = 0 #TODO: performance!  ack
        shift = 0
        while o != 0:
            if o & 1:
                acc ^= self << shift
            shift += 1
            o >>= 1
        return _BinaryFieldInt(acc)
    __rmul__ = __mul__
    def __mod__(self, base):
        q, r = _bf_div(self, base)
        return _BinaryFieldInt(r)
    def __div__(self, o):
        q, r = _bf_div(self, o)
        return _BinaryFieldInt(q)

#the performance is probably terrible
def _bf_div(a, b):
    r = a #remainder
    q = 0 #quotient
    #TODO: optimize by using hex instead of binary
    rlen = len("{0:b}".format(r)) #NOTE: math.log() doesn't work on bignums
    blen = len("{0:b}".format(b))
    sweeper = 1 << (rlen-1)
    while rlen >= blen:
        shift = rlen - blen
        q |= 1 << shift
        r ^= b << shift
        if r == 0: break #great, evenly divisible
        while r and not sweeper & r:
            sweeper >>= 1
            rlen -= 1
    return q, r

def _quadr_solve(beta, f):
    '''
    find a solution of the form z*z + z = b mod f, if a solution exists
    note: z, b, f are all BinaryFieldInts, not regular numbers
    return None if no solution exists
    '''
    z = beta
    m = len("{0:b}".format(f))
    for i in range( (m-1)/2 ):
        z = (z*z) % f
        z = (z*z + beta) % f
    if (z*z + z) % f == beta:
        return z
    raise ValueError("no solution exists for z**2 + z = beta")
    return None


#which specific fields?
#Standard curves recommended by NIST
#see http://csrc.nist.gov/groups/ST/toolkit/documents/dss/NISTReCur.pdf
P192 = Encryptor.make_curve(
    Curve(a = -3, 
          b = 0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1,
          p = 6277101735386680763835789423207666416083908700390324961279),
    G_x = 0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012,
    G_y = 0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811,
    n = 6277101735386680763835789423176059013767194773182842284081)

P224 = Encryptor.make_curve(
    Curve(a = -3,
          b = 0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4,
          p = 26959946667150639794667015087019630673557916260026308143510066298881),
    G_x = 0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21,
    G_y = 0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34,
    n = 26959946667150639794667015087019625940457807714424391721682722368061)

P256 = Encryptor.make_curve(
    Curve(a = -3,
          b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
          p = 115792089210356248762697446949407573530086143415290314195533631308867097853951),
    G_x = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
    G_y = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369)

P384 = Encryptor.make_curve(
    Curve(a = -3,
          b = int("b3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f"\
                  "5013875ac656398d8a2ed19d2a85c8edd3ec2aef", 16),
          p = int("394020061963944792122790401001436138050797392704654466679482"\
                  "93404245721771496870329047266088258938001861606973112319")),
    G_x = int("aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b98"\
              "59f741e082542a385502f25dbf55296c3a545e3872760ab7", 16),
    G_y = int("3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147c"\
              "e9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f", 16),
    n = int("394020061963944792122790401001436138050797392704654466679469052796"\
            "27659399113263569398956308152294913554433653942643"))

P521 = Encryptor.make_curve(
    Curve(a = -3,
          b = int("051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3"\
                  "b8b489918ef109e156193951ec7e937b1652c0bd"\
                  "3bb1bf073573df883d2c34f1ef451fd46b503f00", 16),
          p = int("686479766013060971498190079908139321726943530014330540939446"\
                  "345918554318339765605212255964066145455497729631139148085803"\
                  "7121987999716643812574028291115057151")),
    G_x = int("c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521"\
              "f828af606b4d3dbaa14b5e77efe75928fe1dc127"\
              "a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66", 16),
    G_y = int("11839296a789a3bc0045c8a5fb42c7d1bd998f54449579b4468"\
              "17afbd17273e662c97ee72995ef42640c550b901"\
              "3fad0761353c7086a272c24088be94769fd16650", 16),
    n = int("686479766013060971498190079908139321726943530014330540939446345918"\
        "5543183397655394245057746333217197532963996371363321113864768612440380"\
        "340372808892707005449"))

K163 = Encryptor.make_binary_curve(
    BinaryFieldCurve(a = 1, b = 1, f = [163, 7, 6, 3]),
    G_x = 0x02FE13C0537BBC11ACAA07D793DE4E6D5E5C94EEE8,
    G_y = 0x0289070FB05D38FF58321F2E800536D538CCDAA3D9,
    n = 0x04000000000000000000020108A2E0CC0D99F8A5EF,
    h = 2)

B163 = Encryptor.make_binary_curve(
    BinaryFieldCurve(
        a = 1, #this is the only value of a from 0-4096 which works
        b = 0x20a601907b8c953ca1481eb10512f78744a3205fd,
        f = [163, 7, 6, 3]),
    G_x = 0x3f0eba16286a2d57ea0991168d4994637e8343e36,
    G_y = 0x0d51fbc6c71a0094fa2cdd545b11c5c0c797324f1,
    n = 5846006549323611672814742442876390689256843201587)

#standard curves from Secure Encryption Standard
#http://www.secg.org/collateral/sec2_final.pdf
SECP112_PRIME = (2**128 - 3)/76439

SECP112r1 = Encryptor.make_curve(
    Curve(a = 0xDB7C2ABF62E35E668076BEAD2088,
          b = 0x659EF8BA043916EEDE8911702B22,
          p = SECP112_PRIME),
    G_x = 0x09487239995A5EE76B55F9C2F098,
    G_y = 0xA89CE5AF8724C0A23E0E0FF77500,
    n = 0xDB7C2ABF62E35E7628DFAC6561C5,
    h = 1)

SECP112r2 = Encryptor.make_curve(
    Curve(a = 0x6127C24C05F38A0AAAF65C0EF02C,
          b = 0x51DEF1815DB5ED74FCC34C85D709,
          p = SECP112_PRIME),
    G_x = 0x4BA30AB5E892B4E1649DD0928643,
    G_y = 0xADCD46F5882E3747DEF36E956E97,
    n = 0x36DF0AAFD8B8D7597CA10520D04B,
    h = 4)

SECP128_PRIME = 2**128 - 2**97 - 1

SECP128r1 = Encryptor.make_curve(
    Curve(a = 0xFFFFFFFDFFFFFFFFFFFFFFFFFFFFFFFC,
          b = 0xE87579C11079F43DD824993C2CEE5ED3,
          p = SECP128_PRIME),
    G_x = 0x161FF7528B899B2D0C28607CA52C5B86,
    G_y = 0xCF5AC8395BAFEB13C02DA292DDED7A83,
    n = 0xFFFFFFFE0000000075A30D1B9038A115,
    h = 1)

SECP128r2 = Encryptor.make_curve(
    Curve(a = 0xD6031998D1B3BBFEBF59CC9BBFF9AEE1,
          b = 0x5EEEFCA380D02919DC2C6558BB6D8A5D,
          p = SECP128_PRIME),
    G_x = 0x7B6AA5D85E572983E6FB32A7CDEBC140,
    G_y = 0x27B6916A894D3AEE7106FE805FC34B44,
    n = 0x3FFFFFFF7FFFFFFFBE0024720613B5A3,
    h = 4)

SECP160k1 = Encryptor.make_curve(
    Curve(a = 0,
          b = 7,
          p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFAC73),
    G_x = 0x3B4C382CE37AA192A4019E763036F4F5DD4D7EBB,
    G_y = 0x938CF935318FDCED6BC28286531733C3F03C4FEE,
    n = 0x100000000000000000001B8FA16DFAB9ACA16B6B3,
    h = 1)

SECP160r1 = Encryptor.make_curve(
    Curve(a = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFC,
          b = 0x1C97BEFC54BD7A8B65ACF89F81D4D4ADC565FA45,
          p = 2**160 - 2**31 - 1),
    G_x = 0x4A96B5688EF573284664698968C38BB913CBFC82,
    G_y = 0x23A628553168947D59DCC912042351377AC5FB32,
    n = 0x100000000000000000001F4C8F927AED3CA752257,
    h = 1)

SECP160r2 = Encryptor.make_curve(
    Curve(a = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFAC70,
          b = 0xB4E134D3FB59EB8BAB57274904664D5AF50388BA,
          p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFAC73),
    G_x = 0x52DCB034293A117E1F4FF11B30F7199D3144CE6D,
    G_y = 0xFEAFFEF2E331F296E071FA0DF9982CFEA7D43F2E,
    n = 0x0100000000000000000000351EE786A818F3A1A16B,
    h = 1)

SECP192k1 = Encryptor.make_curve(
    Curve(a = 0,
          b = 3,
          p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFEE37),
    G_x = 0xDB4FF10EC057E9AE26B07D0280B7F4341DA5D1B1EAE06C7D,
    G_y = 0x9B2F2F6D9C5628A7844163D015BE86344082AA88D95E2F9D,
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFE26F2FC170F69466A74DEFD8D,
    h = 1)

SECT163k1 = K163

SECT163r1 = Encryptor.make_binary_curve(
    BinaryFieldCurve(
        a = 0x07B6882CAAEFA84F9554FF8428BD88E246D2782AE2,
        b = 0x0713612DCDDCB40AAB946BDA29CA91F73AF958AFD9,
        f = [163, 7, 6, 3]),
    G_x = 0x0369979697AB43897789566789567F787A7876A654,
    G_y = 0x00435EDB42EFAFB2989D51FEFCE3C80988F41FF883,
    n = 0x03FFFFFFFFFFFFFFFFFFFF48AAB689C29CA710279B, 
    h = 2)

SECT163r2 = Encryptor.make_binary_curve(
    BinaryFieldCurve(
        a = 1,
        b = 0x020A601907B8C953CA1481EB10512F78744A3205FD,
        f = [163, 7, 6, 3]),
    G_x = 0x03F0EBA16286A2D57EA0991168D4994637E8343E36,
    G_y = 0x00D51FBC6C71A0094FA2CDD545B11C5C0C797324F1,
    n = 0x040000000000000000000292FE77E70C12A4234C33, 
    h = 2)

SECT233k1 = Encryptor.make_binary_curve(
    BinaryFieldCurve(a = 0, b = 1, f = [233, 74]),
    G_x = 0x017232BA853A7E731AF129F22FF4149563A419C26BF50A4C9D6EEFAD6126,
    G_y = 0x01DB537DECE819B7F70F555A67C427A8CD9BF18AEB9B56E0C11056FAE6A3,
    n = 0x8000000000000000000000000000069D5BB915BCD46EFB1AD5F173ABDF, 
    h = 4)

SECT233r1 = Encryptor.make_binary_curve(
    BinaryFieldCurve(
        a = 1,
        b = 0x0066647EDE6C332C7F8C0923BB58213B333B20E9CE4281FE115F7D8F90AD,
        f = [233, 74]),
    G_x = 0x00FAC9DFCBAC8313BB2139F1BB755FEF65BC391F8B36F8F8EB7371FD558B,
    G_y = 0x01006A08A41903350678E58528BEBF8A0BEFF867A7CA36716F7E01F81052,
    n = 0x01000000000000000000000000000013E974E72F8A6922031D2603CFE0D7, 
    h = 2)

SECT239k1 = Encryptor.make_binary_curve(
    BinaryFieldCurve(a = 0, b = 1, f = [239, 158]),
    G_x = 0x29A0B6A887A983E9730988A68727A8B2D126C44CC2CC7B2A6555193035DC,
    G_y = 0x76310804F12E549BDB011C103089E73510ACB275FC312A5DC6B76553F0CA,
    n = 0x2000000000000000000000000000005A79FEC67CB6E91F1C1DA800E478A5, 
    h = 4)

SECT283k1 = Encryptor.make_binary_curve(
    BinaryFieldCurve(a = 0, b = 1, f = [283, 12, 7, 5]),
    G_x = 0x0503213F78CA44883F1A3B8162F188E553CD265F23C1567A16876913B0C2AC2458492836,
    G_y = 0x01CCDA380F1C9E318D90F95D07E5426FE87E45C0E8184698E45962364E34116177DD2259,
    n = 0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE9AE2ED07577265DFF7F94451E061E163C61, 
    h = 4)

#curves extracted from libcrvs.a
EC163a02 = SECT163k1

ALL_STD_CIPHERS = [P192, P224, P256, P384, P521, SECP112r1, SECP112r2, SECP128r1, SECP128r2,
SECP160k1, SECP160r1, SECP160r2, SECP192k1, SECT163k1, SECT163r1, SECT163r2, SECT233k1, SECT239k1]

'''
Encryptor.make_curve(
    Curve(a = ,
          b = ,
          p = ),
    G_x = ,
    G_y = ,
    n = ,
    h = )

Encryptor.make_binary_curve(
    BinaryFieldCurve(
        a = ,
        b = ,
        f = ),
    G_x = ,
    G_y = ,
    n = , 
    h = )
'''

def test():
    ecaes_test()
    certicom_mult_test()
    decrypt_test()

    def test_cipher(encryptor):
        private, public = encryptor.gen_keypair()
        cipher, plain = encryptor.encrypt(public)
        assert plain == encryptor.decrypt(private, cipher)
    for encryptor in ALL_STD_CIPHERS:
        print "testing cipher"
        test_cipher(encryptor)

def ecaes_test():
    #test vectors from http://www.secg.org/collateral/gec2.pdf
    r = 501870566195266176721440888203272826969530834326
    priv, pub = SECT163k1.gen_keypair(r)
    assert pub.x == 0x072783FAAB9549002B4F13140B88132D1C75B3886C
    assert pub.y == 0x05A976794EA79A4DE26E2E19418F097942C08641C7
    assert sec_encode(pub) == binascii.unhexlify(
        "02072783FAAB9549002B4F13140B88132D1C75B3886C")
    #OMGWTFBBQ, standards doc test value is wrong -- 0x03 first byte when it should be 0x02
    #or..... is the inverse function wrong?
    ecaes = ECAES(SECT163k1, pub, priv, cipher=XOR)
    plaintext = "abcdefghijklmnopqrst"
    k = 936523985789236956265265265235675811949404040044
    data = ecaes.encrypt(plaintext, k)
    expected_data = binascii.unhexlify(
        "0204994D2C41AA30E52952B0A94EC6511328C502DA9B"+\
        "62A441E4ADF2866BAFEADA50B9DAC1047B2C83B3183301B4"+\
        "14C82DFA91A58311369DF0E2A6F9642C")
    assert data == expected_data
    assert ecaes.decrypt(data) == plaintext

def certicom_mult_test():
    priv = int('00ADB84D68BDCF71B62A4B2808F45DABF8DEA1287B', 16)
    pub = binascii.unhexlify('03005716C55DB50BB7DDD2FDDB6186110A9492465DF5')
    pub = sec_decode(EC163a02.curve, pub)
    assert priv * EC163a02.G == pub

def decrypt_test():
    public_key = sec_decode(EC163a02.curve, binascii.unhexlify('03005716C55DB50BB7DDD2FDDB6186110A9492465DF5'))
    private_key = int('00ADB84D68BDCF71B62A4B2808F45DABF8DEA1287B', 16)
    encrypted = '03027E67B352ACA3B31651D5B812B40A249278AA2E3EB3FCA0BE7D53418B6752A7FD6DB03EA9160B26A3C1B41D3'+\
    '77E50BE769DC4056E7B54C01383855358EE24D662747D649F77138DA111349704BD44B196E217B1DFE8A39FCD2F21C57269398E'+\
    'C0BE57A45AA5150A8C684B930C5C7FF93058CD220E8C923392A1AD303E0262B3C01BB9C3D126D978AF7EB74E766CC1ADC2B900D'+\
    '499ABD1A9A2D27B70DDC89EC51B9EFCD639C4566D43'
    encryptor = ECAES(EC163a02, public_key, private_key, cipher=XOR)
    print binascii.hexlify(encryptor.decrypt(binascii.unhexlify(encrypted)))


