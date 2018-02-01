import math
from math import sqrt
print('''
*--------------------------------------------------------*
|╔════╗=╔╗╔╗=╔═══╗=╔══╗==╔══╗=╔╗===╔══╗=╔════╗=╔══╗=╔═══╗|
|╚═╗╔═╝=║║║║=║╔═╗║=║╔╗║==║╔╗║=║║===║╔╗║=╚═╗╔═╝=║╔╗║=║╔═╗║|
|==║║===║║║║=║╚═╝║=║╚╝╚╗=║║║║=║║===║╚╝║===║║===║║║║=║╚═╝║|
|==║║===║║║║=║╔╗╔╝=║╔═╗║=║║║║=║║===║╔╗║===║║===║║║║=║╔╗╔╝|
|==║║===║╚╝║=║║║║==║╚═╝║=║╚╝║=║╚═╗=║║║║===║║===║╚╝║=║║║║=|
|==╚╝===╚══╝=╚╝╚╝==╚═══╝=╚══╝=╚══╝=╚╝╚╝===╚╝===╚══╝=╚╝╚╝=|
*--------------------------------------------------------*
  beta 1.0
''')
command = input('''
Quadratic function by discriminant - qfd()
Sum of an arithmetic progression - sap()
Calculator - clr()
Exponentiation  - epn()
Excretion from the root - efr()
Command: ''')
if command == 'qfd()':
    print('''Exemples:
ax**2 ± bx ± c = 0''')
    a = int(input('a = '))
    b = int(input('b = '))
    c = int(input('c = '))
    D = b**2 - 4 * a * c
    dis = ('''x-------------x
Discriminant : %s
x-------------x''' % (D))
    print(dis)
    if D == 0:
        x = -b/2*a
        x0_5 = '-%s/2*%s' % (b, a)
        print(x0_5)
        print('x = ', x)
    if D > 0:
        x1 = (-b+math.sqrt(D))/(2*a)
        x1_1 = '-%s+%s/2*%s' % (b, math.sqrt(D), a)
        x2 = -b-math.sqrt(D)/2*a
        x2_1 = '-%s-%s/2*%s' % (b, math.sqrt(D), a)
        print(x1_1)
        print(x2_1)
        print('x1 = ', x1)
        print('x2 = ', x2)
    if D < 0:
        print('No roots')
if command == 'sap()':
    nx = int(input('n1 = '))
    yx = int(input('nx = '))
    yxl = int(input('n = '))
    answer = ((nx + yxl)*yx)/2
    print('S', yx, '=', answer)
if command == 'epn()':
    x = int(input('x = '))
    y = int(input('^y = '))
    print('x^y = ', x**y)
if command == 'clr()':
    x = int(input('x = '))
    y = int(input('y - '))
    fun = input('+, -, *, / = ')
    if fun == '+':
        print(x+y)
    if fun == '-':
        print(x-y)
    if fun == '*':
        print(x*y)
    if fun == '/':
        print(x/y)
if command == 'efr()':
	x = int(input('The number in the root = '))
	print('Answer:', sqrt(x))

print('''Authors:
- D4N1T0S
- Ss0ri0n
''')
