t = {}
t[0,0] = lambda x: x
t[1,0] = lambda x: "Fizz"
t[0,1] = lambda x: "Buzz"
t[1,1] = lambda x: "FizzBuzz"

def tests(x):
    return (x % 3 == 0, x % 5 == 0)

for x in range(1,101):
    print t[tests(x)](x)
