def fizzbuzz(n):
    numb = [ "", str(n) ]
    fizz = [ "", "fizz" ]
    buzz = [ "", "buzz" ]
    isdiv3 = max(0,1-n%3)
    isdiv5 = max(0,1-n%5)
    return  numb[(1 - isdiv3)*(1 - isdiv5)] +\
            fizz[isdiv3] + buzz[isdiv5]


for i in xrange(1,25):
    print fizzbuzz(i)