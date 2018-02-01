#!/usr/bin/python2
from random import randint, choice
from gmpy2 import is_prime # pip install gmpy2
import operator

### Code from ROCA
primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
                       103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167]

prints = [6, 30, 126, 1026, 5658, 107286, 199410, 8388606, 536870910, 2147483646, 67109890, 2199023255550,
8796093022206, 140737488355326, 5310023542746834, 576460752303423486, 1455791217086302986,
147573952589676412926, 20052041432995567486, 6041388139249378920330, 207530445072488465666,
9671406556917033397649406,
618970019642690137449562110,
79228162521181866724264247298,
2535301200456458802993406410750,
1760368345969468176824550810518,
50079290986288516948354744811034,
473022961816146413042658758988474,
10384593717069655257060992658440190,
144390480366845522447407333004847678774,
2722258935367507707706996859454145691646,
174224571863520493293247799005065324265470,
696898287454081973172991196020261297061886,
713623846352979940529142984724747568191373310,
1800793591454480341970779146165214289059119882,
126304807362733370595828809000324029340048915994,
11692013098647223345629478661730264157247460343806,
187072209578355573530071658587684226515959365500926]

def has_fingerprint_real(modulus):
	for i in range(0, len(primes)):
		if (1 << (modulus % primes[i])) & prints[i] == 0:
			return False
	return True
## End code from ROCA

BITS = 1024
MOD = reduce(operator.mul, primes, 1)

residues_p = []
residues_q = []

for p, mask in zip(primes, prints):
	res_p = randint(1, p-1)
	res_q = choice([i for i, x in enumerate(bin(mask)[::-1]) if x == '1']) * pow(res_p, p - 2)

	residues_p.append(res_p)
	residues_q.append(res_q)

def CRT(n, a):
	s = 0
	for n_i, a_i in zip(n, a):
		p = MOD / n_i
		s += a_i * pow(p, n_i - 2) * p
	return s % MOD

def get_prime(residues, bits):
	b = CRT(primes, residues)

	r_min = (1 << (bits - 1)) // MOD
	r_max = (1 << (bits)) // MOD

	while 1:
		p = b + randint(r_min, r_max) * MOD
		if is_prime(p):
			break

	return p

p = get_prime(residues_p, BITS//2)
q = get_prime(residues_q, BITS//2)
N = p * q

print "p =", p
print "q =", q
print "N =", N
print "Vulnerable according to tester:", has_fingerprint_real(N)
