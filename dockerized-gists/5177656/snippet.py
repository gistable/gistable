# Just a test to see how Eliptic Curve DSA works in Bitcoin.
# This isn't production code, this was an exploratory process simply
# for me to learn about it.

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        return None  # modular inverse does not exist
    else:
        return x % m

def testbit(i, offset) :
    """returns a nonzero result, 2**offset, if the bit at 'offset' is one"""
    mask = 1<<offset
    return(i & mask)

class Curve(object):
    def __init__(self, a, b, q):
        self.a = a
        self.b = b
        self.q = q

class ECPoint(object):
    def __init__(self, curve, point) :
        self.curve = curve
        self.point = point
        self.zinv = modinv(point[2], self.curve.q)

    def getX(self):
        return (self.point[0] * self.zinv) % self.curve.q

    def getY(self):
        return (self.point[1] * self.zinv) % self.curve.q

    def add(self, b):
        """Add the point to another point b"""
        # TODO: check for infinity?
        x, y, z = self.point
        bx, by, bz = b.point
        curve = self.curve
        u = (by * z - (y * bz)) % curve.q
        v = (bx * z - (x * bz)) % curve.q

        if v == 0:
            if u == 0:
                return self.twice()
            return ECPoint(self.curve, (None, None, None))

        v2 = v**2
        v3 = v2 * v
        x1v2 = x * v2
        zu2 = u**2 * z
        
        x3 = (((zu2 - (x1v2<<1) * bz) - v3) * v) % curve.q
        y3 = (x1v2 * 3 * u - (y * v3) - (zu2 * u) * bz + u * v3) % curve.q
        z3 = (v3 * z * bz) % curve.q
        return ECPoint(curve, (x3, y3, z3))

    def twice(self):
        x, y, z = self.point
        curve = self.curve
        """Multiply the point by itself"""
        # TODO: check for infinity?
        yz = y * z
        yz2 = (yz * y) % curve.q
        w = (3 * x**2 + curve.a * z**2) % curve.q
        x3 = ((w**2 - ((x<<3) * yz2) << 1) * yz ) % curve.q
        y3 = ((3*w*x - (yz2<<1)<<2) * yz2 - w**2 * w) % curve.q
        z3 = (yz**2 * yz<<3) % curve.q
        return ECPoint(curve, (x3, y3, z3))

    def multiply(self, k):
        """Multiply the point by some other number k"""
        # TODO: check for infinity?
        h = k * 3
        neg = ECPoint(self.curve, (self.point[0], -self.point[1], self.point[2]))
        R = self

        i = h.bit_length() - 2
        while(i > 0) :
            R = R.twice()
            
            hBit = testbit(h, i)
            kBit = testbit(k, i)
            if hBit != kBit :
                if hBit:
                    R = R.add(self)
                else:
                    R = R.add(neg)
            i -= 1
        return R

    def __str__(self):
        return("(%d, %d)" % (self.getX(), self.getY()))

class ECKey(object):
    def __init__(self, private_hex):
        self.__private = int(private_hex, 16)
        curve = Curve(0, 7, 115792089237316195423570985008687907853269984665640564039457584007908834671663)
        self.g = ECPoint(curve, 
          (
           # x: 
           55066263022277343669578718895168534326250603453777594175500187360389116729240,
           # y: 
           32670510020758816978083085130507043184471273380659243275938904335757337482424,
           # z:
           1)
          )

    def get_pub_point(self):
        return self.g.multiply(self.__private)

def test():
    private = "fefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefe"
    key = ECKey(private)
    print key.get_pub_point()

if __name__ == "__main__":
    test()
