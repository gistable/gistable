#-*- coding:utf-8 -*-
'''
DEF CON 2017 Quals - Godzilla (Reverse)
Timing attack on RSA decryption.
Based on http://www.cs.jhu.edu/~fabian/courses/CS600.624/Timing-full.pdf

Another solutions:
https://gist.github.com/nneonneo/367240ae2d8e705bb9173a49a7c8b0cd by b2xiao
https://gist.github.com/Riatre/caac24840b176cf843b3f66ad9a5eeaf by riatre

(We didn't solve the challenge during the CTF, upsolved later).

- The challenge binary leaks number of modular subtractions in Montgomery reductions.
- By guessing the secret exponent bit-by-bit, we can predict for any message whether a particular subtraction was made.
- As in the paper, attacking squaring reduction is more preferable.
- For correct bit guess our prediction results in observable difference in distributions.
- For incorrect guess, the difference should be smaller.

A pool of ~200k signatures with timings is enough (at least for specified local N,d).
Possibly we can use less signatures with error correction but is a bit tedious to implement.

For local testing:
/home/godzilla/private.key:
modulus: 621765037979243120244866560860969322461463809129505955186452584191781197841649371514421546962009613592757586308279377033451677755878455977108757795291066809685046961038952999040910695459046816930080946215577583202802372206660787951
privateExponent: 13073412306565711272982073040670395751283963699596551661609955613108236425619006575627094491869466828369012221078305566175300329355043186187545693870963542712368839629270596359194127129928012640315145165189316557655977123753630961

After collecting 200k signatures:
$ time pypy rsa_timing_attack_d.py
Address: 127.0.0.1:3030
Pool: pool_local
Loaded 200000 items
...
Current minimum delta delta: 8.77617921084 avg 160.586027156

Full d recovered!
13073412306565711272982073040670395751283963699596551661609955613108236425619006575627094491869466828369012221078305566175300329355043186187545693870963542712368839629270596359194127129928012640315145165189316557655977123753630961

real    11m47.278s
user    11m45.860s
sys 0m2.996s

(minimum delta is quite low, seems we need more signatures to be sure)
'''

from sock import Sock
from libnum import invmod
from struct import pack, unpack

if 1:
    pool_fname = "pool_local"
    addr = "127.0.0.1:3030"

    # p = 0x8955632da8661739b0d729001befe603cca087282fadea8fc899f6ce49061acd9347b387d54ea007ec57d0698c8d978d
    # q = 0xbf1d3b6a1dccf82a333dec6285ab7bc6839194e6184c15d5dbe3e44098879040d2a2816b27078f1434f422127cf7236b
    # n = 0x6686638ae80377047e22f72267e705c9fa726016b08ad44278c6a006fb8dfcdd01e2b6cd8df5dab59a9af240fee86f4c598d2ffc7e4e55dcbb227df17bd9b220de2f7ea20f4506143388387b7827716de995f4f135718a24c6971e449ff19eef
    # d = 0x227dd3bf478ee2db801403506fe428ee6a735020520462a47a3d5859010823a9b698af27383b1df93aaa2615f7abfac5265be9ce18a2147352e60fe6ff453781e702f7c6ffa51da43c3b207307b774256e06b9f0ad05a6faa1a148799321cf1

    N = 0x6686638ae80377047e22f72267e705c9fa726016b08ad44278c6a006fb8dfcdd01e2b6cd8df5dab59a9af240fee86f4c598d2ffc7e4e55dcbb227df17bd9b220de2f7ea20f4506143388387b7827716de995f4f135718a24c6971e449ff19eef
    privexp = 0x227dd3bf478ee2db801403506fe428ee6a735020520462a47a3d5859010823a9b698af27383b1df93aaa2615f7abfac5265be9ce18a2147352e60fe6ff453781e702f7c6ffa51da43c3b207307b774256e06b9f0ad05a6faa1a148799321cf1
else:
    pool_fname = "pool_task"
    addr = "godzilla_3751355706cae43e14bd797a16946483.quals.shallweplayaga.me:11577"

    N = 1003103838556651507628555636330026033778617920156717988356542246694938166737814566792763905093451568623751209393228473104621241127455927948500155303095577513801000908445368656518814002954652859078574695890342113223231421454500402449
    privexp = None

print "Address:", addr
print "Pool:", pool_fname


## Montgomery stuff

RE = 768
R = 2**RE
RMASK = R - 1
Ni = -invmod(N, R) % R
Ri = invmod(R, N)

assert R > N
assert N * Ni % R == R - 1
assert R * Ri % N == 1

def redc(T):
    '''From wikipedia
    take (aR % N) * (bR % N)
    return abR % N, was_reduced
    '''
    m = ((T & RMASK) * Ni) & RMASK
    t = (T + m * N) >> RE
    if t >= N:
        return (t - N), 1
        t -= N
    return t, 0

def to_mont(m):
    return (m * R) % N

def mont_square(x):
    x = x * x
    x, flag = redc(x)
    return x, flag

def mont_mul_cond(x, m0r, bit):
    flag = 0
    if bit:
        x = (x * m0r)
        x, flag = redc(x)
    return x, flag

def mont_exp_one_round(x, m0r, bit):
    x, flag = mont_mul_cond(x, m0r, bit)
    x, flag = mont_square(x)
    return x, flag


## Challenge specific

f = Sock(addr)

def bignum2ints(n):
    res = []
    for i in xrange(0x18):
        res.append(n % 2**32)
        n >>= 32
    return res

def decryptTime(bignum):
    global f
    try:
        f.send(pack("<I", 0x41424344))
        f.send(chr(0x80 | 0x01))

        p = "".join(pack("<I", c) for c in bignum2ints(bignum))
        assert len(p) == 0x60
        f.send(p)

        buf = "WWWWXXXXYYYYZZZZ"
        f.send(chr(len(buf)))
        f.send(buf)

        b = f.read_nbytes(16)
        assert b[12:] == "\x02\x00\xff\x00", b.encode("hex")
        vals = unpack("<3I", b[:12])
        # vals[0] - some rdtsc difference
        # vals[1] - leaked number of reductions
        # vals[2] - some rdtsc difference
        return vals[1]
    except EOFError:
        print "EOF, retry"
        f = Sock(addr)
        return decryptTime(bignum)


# loading / filling pool of signatures with timings
# pool: list of (message, timing) pairs

import ast
pool = []
for line in open(pool_fname):
    pool.append(ast.literal_eval(line))
    if len(pool) >= 200000:
        break
print "Loaded", len(pool), "items"

if "y" in raw_input("Collect? [y/N]"):
    fp = open(pool_fname, "a")
    itr = 0
    while 1:
        itr += 1
        if itr % 100 == 0:
            print itr
        m = random.randint(1, N-1)
        t = decryptTime(m)
        pool.append((m, t))
        fp.write(`pool[-1]` + "\n")
        fp.flush()

def avg(l):
    return sum(l)/float(len(l))

# maintain partially exponentiated messages
# (up to known bits of d)
pool = [
    (
        mont_square(to_mont(m))[0],
        to_mont(m),
        time,
    )
    for m, time in pool
]

current_d = 1
mindiff = 1e9
sumdiff = 0
for di in xrange(768):
    print "di", di
    sm = 0
    goods = [0] * (2**1)

    MS = [[], []], [[], []]
    pool2 = []
    for mcur, m0r, real in pool:
        if current_d > 1:
            # partially exponentiate using previously guessed bit
            mcur, _ = mont_exp_one_round(mcur, m0r, current_d & 1)
        pool2.append((mcur, m0r, real))

        for bit in xrange(2):
            _, e = mont_exp_one_round(mcur, m0r, bit)
            MS[bit][e].append(real)
    pool = pool2

    m0 = avg(MS[0][0]), avg(MS[0][1])
    m1 = avg(MS[1][0]), avg(MS[1][1])
    delta0 = m0[1] - m0[0]
    delta1 = m1[1] - m1[0]
    print m0, delta0
    print m1, delta1
    if delta0 > delta1:
        guessed = 0
    else:
        guessed = 1
    mindiff = min(mindiff, abs(delta0 - delta1))
    sumdiff += abs(delta0 - delta1)
    print "Current minimum delta delta:", mindiff, "avg", sumdiff / float(di+1)
    print

    current_d <<= 1
    current_d |= guessed
    print bin(current_d)[:100] + "..."
    if pow(31337, 0x10001 * current_d, N) == 31337:
        print "Full d recovered!"
        print current_d
        break

    if privexp:
        print bin(privexp)[:100] + "..."
        realbit = int(bin(privexp)[2:][1+di])
        print "Correct?", guessed, "=?", realbit, ":", guessed == realbit
        if guessed != realbit:
            print "FAIL"
            quit()
