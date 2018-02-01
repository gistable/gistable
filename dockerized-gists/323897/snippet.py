# refactoring of http://sandrotosi.blogspot.com/2010/03/project-euler-problem-14.html

cache = {1: 1}

def collatz(n):
    if n not in cache:
        if n % 2 == 0:
            cache[n] = 1 + collatz(n/2)
        else:
            cache[n] = 1 + collatz(3*n + 1)
    return cache[n]
