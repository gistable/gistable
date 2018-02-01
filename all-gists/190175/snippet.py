# Hello world:
print "Hello, World!"


# Print the numbers 1 to 10:
for i in range(1, 11):
    print i


# Print the numbers less than 100, which are divisable by 3:
for i in range(1, 100):
    if i % 3 == 0:
        print i


# Print the numbers less than 100, which are divisable by 3, or 5:
for i in range(1, 100):
    if i % 3 == 0 or i % 5 == 0:
        print i


# Print the first ten values of the Fibonacci Sequence (1, 1, 2, 3, 5, 8, 13, 21, 34, 55):
a = b = 1
for _ in range(0, 10): # We generally use the _ variable for something we don't care about.
    print a
    a, b = b, a + b


def fibonacci(n):
    """Print the first N values of the Fibonacci Sequence."""
    a = b = 1
    for _ in range(1, n + 1):
        print a
        a, b = b, a + b

fibonacci(6)


def fibonacci2(n):
    """Return the first N values of the Fibonacci Sequence."""
    a = b = 1
    fib = []
    for _ in range(1, n + 1):
        fib.append(a)
        a, b = b, a + b
    return fib

print fibonacci2(8) # -> [1, 1, 2, 3, 5, 8, 13, 21]


def fibonacci3(n):
    """Return the first N values of the Fibonacci Sequence."""
    fib = [1, 1]
    for _ in range(2, n):
        next = fib[len(fib) - 1] + fib[len(fib) - 2]
        fib.append(next)
    return fib

print fibonacci3(12) # -> [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]


def sum_list(the_list):
    """Sum all of the items in a list."""
    total = 0
    for n in the_list:
        total += n
    return total

print sum_list([6, 8, 3, 5, 1, 4, 7, 9, 2, 0]) # -> 45


def count_zeros(the_list):
    """Count the number of zeros in a list."""
    zeros = 0
    for n in the_list:
        if n == 0:
            zeros += 1
    return zeros

print count_zeros([6, 8, 3, 0, 1, 4, 0, 9, 2, 0]) # -> 3


def sum_list2(the_list):
    """Sum all of the items in a list, using Python's builtin sum function."""
    return sum(the_list)

print sum_list2([6, 8, 3, 5, 1, 4, 7, 9, 2, 0]) # -> 45


# Count the number of zeros in a list, using Python's builtin filter function:
def equals_zero(n):
    return n == 0

def count_zeros2(the_list):
    return len(filter(equals_zero, the_list))

print count_zeros2([6, 8, 3, 0, 1, 4, 0, 9, 2, 0]) # -> 3


# Double all of th numbers in a list, using Python's builtin map function:
def doubler(the_list):
    the_doubler = lambda n: n * 2
    return map(the_doubler, the_list)

print doubler([0, 1, 2, 3, 4, 5, 'a', ['Hey']]) # -> [0, 2, 4, 6, 8, 10, 'aa', ['Hey', 'Hey']]
