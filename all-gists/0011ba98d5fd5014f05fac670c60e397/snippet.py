import json
from random import randint


class RSA(object):

    def __init__(self):
        self.p, self.q = self.gen_p_q()
        self.N = self.p * self.q
        self.phi = self.euler_function(self.p, self.q)
        self.public_key_pair = (self.gen_public_exponent(), self.N)
        self.private_key_pair = (self.gen_private_exponent(), self.N)

    def encrypt(self, message, public_key_pair):
        return self.crypt(message, public_key_pair, encrypt=True)

    def decrypt(self, cipher, private_key_pair):
        return self.crypt(cipher, private_key_pair, encrypt=False)

    def crypt(self, message, key_pair, encrypt=True):
        if encrypt:
            msg = [ord(c) for c in message]
            r = [pow(i, key_pair[0], key_pair[1]) for i in msg]
            return b64encode(bytes(json.dumps(r), 'utf8')).decode('utf8'), r
        else:
            msg = json.loads(b64decode(message).decode('utf8'))
            r = [pow(i, key_pair[0], key_pair[1]) for i in msg]
            return ''.join(chr(i) for i in r), r

    def get_public_key_pair(self):
        return self.public_key_pair

    def get_private_key_pair(self):
        return self.private_key_pair

    def get_phi(self):
        return self.phi

    def get_p_q(self):
        return self.p, self.q

    def gen_public_exponent(self):
        for e in reversed(range(self.phi)):
            if self.fermat_primality(e):
                self.e = e
                return e

    def gen_private_exponent(self):
        self.d = self.mod_multiplicative_inv(self.e, self.phi)[0]
        return self.d

    def euler_function(self, p, q):
        return (p - 1) * (q - 1)

    def gen_p_q(self):
        p_c, q_c = randint(2, 100000), randint(2, 100000)
        p = q = None
        gen1 = gen2 = self.eratosthenes_sieve()
        bigger = max(p_c, q_c)

        for i in range(bigger):
            if p_c > 0:
                p = next(gen1)
            if q_c > 0:
                q = next(gen2)
            p_c -= 1
            q_c -= 1

        return p, q

    def fermat_primality(self, n):
        if n == 2:
            return True
        if not n & 1:
            return False
        return pow(2, n - 1, n) == 1

    def extended_euclide(self, b, n):
        # u*a + v*b = gcd(a, b)
        # return g, u, v
        x0, x1, y0, y1 = 1, 0, 0, 1
        while n != 0:
            q, b, n = b // n, n, b % n
            x0, x1 = x1, x0 - q * x1
            y0, y1 = y1, y0 - q * y1
        return b, x0, y0

    def mod_multiplicative_inv(self, a, b):
        g, u, v = self.extended_euclide(a, b)
        return b + u, a - v

    def eratosthenes_sieve(self):
        D = {}
        q = 2

        while True:
            if q not in D:
                yield q
                D[q * q] = [q]
            else:
                for p in D[q]:
                    D.setdefault(p + q, []).append(p)
                del D[q]
            q += 1
            
    def print_info(self):
        print('p = %d\nq = %d' % (self.p, self.q))
        print('N = %d\nphi = %d' % (self.N, self.phi))
        print('e = %d\nd = %d' % (self.e, self.d))

# ======================================================

rsa = RSA()
message = 'hello!'
cipher = rsa.encrypt(message, rsa.get_public_key_pair())
print(cipher[0])
deciphered = rsa.decrypt(cipher[0], rsa.get_private_key_pair())
print(deciphered[0])