def fizz():
    while True:
        yield ''
        yield ''
        yield 'fizz'

def buzz():
    while True:
        yield ''
        yield ''
        yield ''
        yield ''
        yield 'buzz'

f = fizz()
b = buzz()
for i in range(1, 101):
    print((f.next() + b.next()) or i)
