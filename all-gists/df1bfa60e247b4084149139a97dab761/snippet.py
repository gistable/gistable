from fractions import gcd, Fraction


def intSqrt(n):
    """
    Computes the integer square root of n, i.e.
    the greatest x : x*x <= n
    """
    x = n
    y = (x + n // x) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def isSquare(n):
    """
    Checks if n is a perfect square
    """
    return intSqrt(n)**2 == n


def inverseMod(a, b):
    """
    Computes the integer x such that
    a*x = 1 mod b.
    """
    if gcd(a, b) != 1:
        return 0
    x2 = 1
    x1 = 0
    mod = b
    while b > 0:
        r = a % b
        x = x2 - (a // b) * x1
        a = b
        b = r
        x2 = x1
        x1 = x
    return x2 % mod


class ContinuedFraction(Fraction):
    def __init__(self, num, den):
        super(Fraction, self).__init__()

    def expand(self):
        fractPart = Fraction(1, 1)
        x = Fraction(self)
        while fractPart.numerator != 0:
            intPart = int(x)
            fractPart = x - intPart
            if fractPart != 0:
                x = 1 / fractPart
            yield intPart

    @classmethod
    def nextConvergent(self, n, h1, h2, k1, k2):
        if type(n) != int:
            raise Exception("n must be an integer.")
        return Fraction(n * h1 + h2, n * k1 + k2)

    def convergents(self):
        """
        Generates a list of convergents.
        """
        h1 = 1
        h2 = 0
        k1 = 0
        k2 = 1
        for i in self.expand():
            f = self.nextConvergent(i, h1, h2, k1, k2)
            h2 = h1
            h1 = f.numerator
            k2 = k1
            k1 = f.denominator
            yield f


def WienersAttack(e, n):
    """
    Tries to recover d from (e,n).
    """
    cf = ContinuedFraction(e, n)
    for conv in cf.convergents():
        # print(conv)
        k = conv.numerator
        d = conv.denominator
        if k != 0 and d % 2 != 0:
            if (e * d - 1) % k == 0:  # phi is an integer
                phi = (e * d - 1) // k
                b = n - phi + 1     # b is even (n+1 even - phi even)
                if isSquare(b ** 2 - 4 * n):
                    deltaRoot = intSqrt(b ** 2 - 4 * n)
                    if deltaRoot % 2 == 0:  # deltaRoot is even
                        p = (b + deltaRoot) // 2
                        q = (b - deltaRoot) // 2
                        d = inverseMod(e, phi)
                        return (n, e, d, p, q)
    # The attack has failed
    return False


# Example (from Wikipedia)
# https://en.wikipedia.org/wiki/Wiener%27s_attack
print(WienersAttack(17993, 90581))
