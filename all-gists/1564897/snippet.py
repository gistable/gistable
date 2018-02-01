import sys

def prime(number):
    n = abs(number)

    if n < 1:
        return False

    if n==2:
        return True

    if not n & 1:
        return False

    for x in range(3, int(n**0.5)+1, 2):
        if n % x == 0:
            return False

    return True



if __name__=="__main__":
    
    if len(sys.argv[1:]) == 0:
        print "usage: pyPrime.py <number>"
        sys.exit(0)



    try:
        value = int(sys.argv[1])
    except:
        print "The parameter must be a number"
        print "usage: pyPrime.py <number>"
        sys.exit(0)

    if value < 0:
        print "The parameter must be a positive number"
        print "usage: pyPrime.py <number>"
        sys.exit(0)


    if value % 2 != 0:
        print "This validations works only for Even numbers"
        print "usage: pyPrime.py <number>"
        sys.exit(0)


    primes=[x for x in range(3, value, 2) if prime(x)]


    expressions=[]
    while len(primes) > 0:
        rest = value - primes[::-1][0]
        
        if rest in primes:
            expressions.append("%s + %s" %(primes[::-1][0], rest))
            primes.remove(rest)

        primes.pop()

    print "Goldbach's conjecture"  
    print "%s = %s" %(value, ", ".join(expressions))
