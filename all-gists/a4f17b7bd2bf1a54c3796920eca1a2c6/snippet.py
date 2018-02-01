_x = float(input('base: '))
x = _x
n = int(input('exponent: '))
i = 0
if n == 0:
    print('The result is 1')
else:
    while i < n - 1:
        x = x * _x
        i += 1
print(x)
