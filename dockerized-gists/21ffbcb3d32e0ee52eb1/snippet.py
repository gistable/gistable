import hashlib
import itertools
import string
import time
import console

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def encrypt(data):
    return hashlib.md5(data).hexdigest()

password = encrypt('pass')

def crack(hash, charset, maxlength):
    attempts = 0
    for attempt in (''.join(candidate) for candidate in itertools.chain.from_iterable(itertools.product(charset, repeat=i) for i in range(1, maxlength + 1))):
        attempts += 1
        print 'attempts:', attempts
        console.clear()
        if encrypt(attempt) == hash:
            print 'Found:', attempt
            break
            
s = time.time()
print len(string.ascii_letters+string.digits)
crack(encrypt('pass'), string.ascii_letters+string.digits, 3)
print 'finished in', round(s-time.time(), 3)/-1, 'seconds'
