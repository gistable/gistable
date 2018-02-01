from multiprocessing import Pool


def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


def done(*args, **kwargs):
    print '==>', args, kwargs


p = Pool(5)
for x in range(10, 40):
    p.apply_async(fib, args=(x,), callback=done)

print 'Waiting to finish work...'
p.close()
p.join()
print 'Done. Ciao.'
