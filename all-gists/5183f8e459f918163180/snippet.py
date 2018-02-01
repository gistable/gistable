'''
Test performance of tuple adding on Macbook Air 2012:
unpacking   :    1,598 min |    2,136 max |    1,787 avg (µs)
index       :    2,622 min |    5,016 max |    3,402 avg (µs)
map add     :    7,849 min |   10,670 max |    8,886 avg (µs)
map sum zip :   11,254 min |   16,354 max |   12,854 avg (µs)
'''
import timeit

def show_result(func, result):
    print('{:12}: {:8,.0f} min | {:8,.0f} max | {:8,.0f} avg (µs)'.format(
        func, min(result) * 1e6, max(result) * 1e6, (sum(result) / float(len(result))) * 1e6))


statement = "cx, cy = c; bx, by=b; c = (cx + bx, cy + by)"
setup_statement = "c = (0, 0); b=(1, -1)"
show_result('unpacking', timeit.repeat(statement, setup_statement, repeat=7, number=10000))

statement = "c = (c[0] + b[0], c[1] + b[1])"
setup_statement = "c = (0, 0); b=(1, -1)"
show_result('index', timeit.repeat(statement, setup_statement, repeat=7, number=10000))

statement = "c = tuple(map(add, c, b))"
setup_statement = "from operator import add; c = (0, 0); b=(1, -1)"
show_result('map add', timeit.repeat(statement, setup_statement, repeat=7, number=10000))

statement = "c = tuple(map(sum,zip(c, b)))"
setup_statement = "c = (0, 0);b=(1, -1)"
show_result('map sum zip', timeit.repeat(statement, setup_statement, repeat=7, number=10000))
