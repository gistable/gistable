# This is a solution to a blog post I just found at https://blog.svpino.com/2015/05/07/five-programming-problems-every-software-engineer-should-be-able-to-solve-in-less-than-1-hour
# I wrote it in Python because it shines for such challenges.
# It took me approximately 35 minutes (edit: added 5 minutes because of a bug in problem #4), so if I trust the internet, I'm definitely a Software Engineer.
# How cool is that? :-)

# Problem 1
# ---------
# Write three functions that compute the sum of the numbers in a given list 
# using a for-loop, a while-loop, and recursion.
def problem1_1(l):
     s = 0
     for n in l:
             s += n
     return s
     
def problem1_2(l):
     s, i = 0, 0
     while i < len(l):
             s += l[i]
             i += 1
     return s
     
def problem1_3(l, accu=0):
    if len(l):
        it = iter(l)
        accu += it.next()
        return problem1_3(list(it), accu)
    else:
        return accu
        
def problem1_real_programmer(l):
    return sum(l)

# Problem 2
# ---------
# Write a function that combines two lists by alternatingly taking elements. 
# For example: given the two lists [a, b, c] and [1, 2, 3], the function 
# should return [a, 1, b, 2, c, 3]
def problem2(l1, l2):
    result = []
    for (e1, e2) in zip(l1, l2):
        result.append(e1)
        result.append(e2)
    return result
    
def problem2_real_programmer(l1, l2):
    from itertools import chain
    return [x for x in chain.from_iterable(zip(l1, l2))]
    
# Problem 3
# ---------
# Write a function that computes the list of the first 100 Fibonacci numbers. 
# By definition, the first two numbers in the Fibonacci sequence are 0 and 1, 
# and each subsequent number is the sum of the previous two. As an example, 
# here are the first 10 Fibonnaci numbers: 0, 1, 1, 2, 3, 5, 8, 13, 21, and 34.    
def fibonacci():
    a, b = 0, 1
    while 1:
        yield a
        a, b = b, a + b

def problem3():
    fib = fibonacci()
    return [fib.next() for _ in range(100)]
    
# Problem 4
# ---------
# Write a function that given a list of non negative integers, arranges them 
# such that they form the largest possible number. For example, given 
# [50, 2, 1, 9], the largest formed number is 95021.
def problem4(l):
    # convert one time to string to avoid multiple casting during comparison
    ls = sorted(map(str, l), cmp=lambda e,f: cmp(e+f, f+e), reverse=True)
    return int(''.join(ls))
    
# Problem 5
# ---------
# Write a program that outputs all possibilities to put + or - or nothing 
# between the numbers 1, 2, ..., 9 (in this order) such that the result is 
# always 100. For example: 1 + 2 + 34 – 5 + 67 – 8 + 9 = 100.
def problem5():
   from itertools import product
   results, numbers = [], range(1, 10)
   for perm in product(['+','-', ''], repeat=8): # iterate on arrangements of operators
       tuples = zip(numbers, perm + ('', )) # add something for digit 9
       expression = ''.join([str(e1) + e2 for (e1, e2) in tuples]) # create expression as string
       if eval(expression) == 100: # you know what this does
           results.append(expression + ' = 100')
   return results

    
# Check the solutions
# -------------------
assert(problem1_1([1,2,3,4,5,6]) == sum([1,2,3,4,5,6]))
assert(problem1_2([1,2,3,4,5,6]) == sum([1,2,3,4,5,6]))
assert(problem1_3([1,2,3,4,5,6]) == sum([1,2,3,4,5,6]))
assert(problem1_real_programmer([1,2,3,4,5,6]) == sum([1,2,3,4,5,6]))
assert(problem2(['a', 'b', 'c'], [1, 2, 3]) == ['a', 1, 'b', 2, 'c', 3])
assert(problem2_real_programmer(['a', 'b', 'c'], [1, 2, 3]) == ['a', 1, 'b', 2, 'c', 3])
assert(len(problem3()) == 100)
assert(problem3()[50] == 12586269025)
assert(problem4([50, 2, 1, 9]) == 95021)
assert(len(problem5()) == 11)
print "It works!"