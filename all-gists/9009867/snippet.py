def is_palindrome(x):
    x = str(x)
    return x == x[::-1]

def find_palindromes(m, n):
    for i in xrange(m, n):
        for j in xrange(i, n):
            x = i * j
            if is_palindrome(x):
                yield x

print max(find_palindromes(100, 1000))
