import math

def IsPrime(n):
    if(n == 2):
        return True
    elif(n % 2 == 0 or n < 2):
        return False
    length = math.floor(math.sqrt(n) / 2) + 1
    ls = [True] * length
    ls[0] = False
    for i in range(length):
        if(ls[i] == False):
            continue
        else:
            if(n % (2 * i + 1) == 0):
                return False
            else:
                for l in [x for x in range(1, math.floor((2 * length - 1) / (2 * i + 1)) + 1) if x % 2 != 0]:
                    ls[math.floor(i * l + (l - 1) / 2)] = False
    return True
