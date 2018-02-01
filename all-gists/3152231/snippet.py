# My Second Python program
# Based on this spec: http://www.codinghorror.com/blog/2007/02/why-cant-programmers-program.html

import time
import random

def fbFilter(n): return n % 5 == 0 or n % 3 == 0

def fbTranslator(n):
    output = '{0}'.format(n)
    if n % 15 == 0:
        return '{0}, uh I mean "FizzBuzz"! Said the child'.format(n)
    elif n % 5 == 0:
        return 'Buzz!'
    elif n % 3 == 0:
        return 'Fizz!'
    return output

def fbPrinter(sleep, n, i):
    time.sleep(sleep)
    print(n)

def fbSimulateProficiency(n):
    if n % 15 == 0:
        return random.randint(3, 5)
    elif n % 5 == 0:
        if i < 20:
            return random.randint(2, 3)
    elif i < 20:
        return random.randint(1,3)
    return random.randint(0, 1)


[fbPrinter(fbSimulateProficiency(i), fbTranslator(i), i) for i in range(1, 100)]