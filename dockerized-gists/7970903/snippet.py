import random
def isProbablePrime(n):
    '''
    Miller-Rabin primality test.
    from http://rosettacode.org/wiki/Miller-Rabin_primality_test#Python
    '''
    _mrpt_num_trials = 5 # number of bases to test
    assert n >= 2
    # special case 2
    if n == 2:
        return True
    # ensure n is odd
    if n % 2 == 0:
        return False
    # write n-1 as 2**s * d
    # repeatedly try to divide n-1 by 2
    s = 0
    d = n-1
    while True:
        quotient, remainder = divmod(d, 2)
        if remainder == 1:
            break
        s += 1
        d = quotient
    assert(2**s * d == n-1)
 
    # test the base a to see whether it is a witness for the compositeness of n
    def try_composite(a):
        if pow(a, d, n) == 1:
            return False
        for i in range(s):
            if pow(a, 2**i * d, n) == n-1:
                return False
        return True # n is definitely composite
 
    for i in range(_mrpt_num_trials):
        a = random.randrange(2, n)
        if try_composite(a):
            return False
 
    return True # no base tested showed n as composite

def isPrime(n):
    '''
    Slow but confirmed prime tester
    '''
    return not any(n%i == 0 for i in xrange(2, int(n**0.5) +1))

def getLargePrime(bits):
    '''
    Randomly generates a large number of specified bits
    and then tests if it's prime
    '''
    while True:
        p = random.getrandbits(bits)
        if isProbablePrime(p):
            return p

def egcd(a, b):
    '''
    Extended Eucledian Algorithm
    from http://en.wikibooks.org/wiki/Algorithm_Implementation/Mathematics/Extended_Euclidean_algorithm
    '''
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    return b, x, y

def getED(phi):
    '''
    Finds radnom e and corresponding d based on phi
    '''
    while True:
        i = random.randrange(2, phi)
        gcd, x, y = egcd(i, phi)
        if gcd == 1:
            return i, x % phi
        
def keyGen(bits):
    '''
    Generates public key and private key of specified bit length
    Returns (public_key, private_key)
    public_key = (e, n)
    private_key = (d, n)
    '''
    p, q = getLargePrime(bits), getLargePrime(bits)
    n = p*q
    phi = (p-1) * (q-1)
    e, d = getED(phi) 
    return (e,n), (d, n)

def encrypt(m, public_key):
    e, n = public_key
    return pow(m, e, n)

def decrypt(c, private_key):
    return encrypt(c, private_key)

if __name__ == '__main__':
    BITLENGTH = 512
    print 'Generating New Keys of length %s' % BITLENGTH
    public_key, private_key = keyGen(BITLENGTH)
    print 'Public Key(e,n):', public_key
    print 'Private Key(d,n):', private_key
    print 'Generating a random %s bit message' % BITLENGTH
    message = random.getrandbits(BITLENGTH)
    print 'Messsage:', message
    print 'Encrypting random message of %s bit length' % BITLENGTH
    cipher = encrypt(message, public_key)
    print 'Encrypted:', cipher
    print 'Decrypting it back:', decrypt(cipher, private_key)
    print 'Decryption successfull:', decrypt(cipher, private_key) == message
