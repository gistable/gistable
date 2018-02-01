Python Cheatsheet
=================

 ################################ Input & Output ###############################
name = input('please enter your name: ')
print('hello,', name)
ageStr = input('please enter your age: ')
age = int(ageStr)


#################################### String ####################################
"I'm OK"
'I\'m \"OK\"!'
r'\\\t\\'
'''line1
line2
line3'''


################################ Python's Null ################################
None


################################### Division ###################################
10 / 3
10 // 3
10 % 3


############################## Unicode <--> char ##############################
ord('A')
chr(66)
'\u4e2d\u6587'


#################################### Bytes ####################################
b'ABC'


############################### Encode & Decode ###############################
'中文'.encode('utf-8')
b'\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8')
'ABC'.encode('ascii')
b'ABC'.decode('ascii')


################################ String format ################################
'Hi, %s, you have $%d.' % ('Michael', 1000000)
'%.2f' % 3.1415926
'Age: %s. Gender: %s' % (25, True) # bool->true

%d  int
%f  float
%s  str
%x  hex int

a = 'abc'
b = a.replace('a', 'A')
b # = 'Abc'
a # = 'abc'


##################################### List #####################################
classmates = ['Michael', 'Bob', 'Tracy']
len(classmates)

classmates[-1]  = 'Sarah'

classmates.append('Adam')
classmates.insert(1, 'Jack')
classmates.pop()

L0 = []
L1 = ['Apple', 123, True]
L2 = ['python', 'java', ['asp', 'php'], 'scheme']
len(L2) # = 4;


################################ Slice of list ################################
L = ['Michael', 'Sarah', 'Tracy', 'Bob', 'Jack']
L[0:3] # = ['Michael', 'Sarah', 'Tracy']
L[:3] # same
L[:-2] # same

L = list(range(100))
L[:10:2] # = [0, 2, 4, 6, 8]
L[::5]   # [0, 5, 10, 15, 20, 25, 30 ... 90, 95]
L[:]     # [0, 1, 2, 3, ..., 99]


#################################### Tuple ####################################
classmates = ('Michael', 'Bob', 'Tracy')
classmates[-1]
t = ()
t = (1,)  # attention comma!
t = (1, 2)


################################# Other slice #################################
(0, 1, 2, 3, 4, 5)[:3]  # = (0, 1, 2)
'ABCDEFG'[:3]


################################ 'if' statement ################################
age = 20
if age >= 6:
    print('teenager')
elif age >= 18:
    print('adult')
else:
    print('kid')

if x:
    print('True')
    # x -> True when x is:
    # non-zero int, non-empty str, non-empty list/tuple


############################### 'for' statement ###############################
names = ['Michael', 'Bob', 'Tracy']
for name in names:
    print(name)

list(range(5)) # = [0, 1, 2, 3, 4]

sum = 0
for x in range(101):
    sum = sum + x


############################## 'while' statement ##############################
sum = 0
x = 100
while x > 0:
    sum = sum + x
    x = x - 1


################################ Key-value dict ################################
d = {'Michael': 95, 'Bob': 75, 'Tracy': 85}
d['Michael']    # Get (= 95)
d['Adam'] = 67  # Insert
d['Adam'] = 90  # Replace

'Thomas' in d   # False
d.get('Thomas', -1)  # -1

d.pop('Bob')    # Delete


##################################### Set #####################################
s = set([1, 2, 3])
set([1, 1, 2, 2, 3, 3])  # {1, 2, 3}
s.add(4)  # no effect if duplicated
s.remove(4)
s1 & s2  # intersection
s1 | s2  # union


##################################### Math #####################################
abs(-100)
max(3, 2, -3, -5)


############################### Type convertion ###############################
int('123')
int(12.34)
float('12.34')
str(1.23)
str(100)
bool(1)  # True
bool('')  # False


############################### 'pass' statement ###############################
def nop():
    pass

if age >= 18:
    pass


############################ 'isinstance' statement ############################
if not isinstance(x, (int, float)):
    raise TypeError('bad operand type')


############################# return multi values #############################
def move(x, y, step, angle=0):
    nx = x + step * math.cos(angle)
    ny = y - step * math.sin(angle)
    return nx, ny
x, y = move(100, 100, 60, math.pi / 6)
ret = move(...)  # -> tuple


##################### Named arguments & default arguments #####################
def enroll(name, gender, age=6, city='Beijing'):
    print('name:', name)
    print('gender:', gender)
    print('age:', age)
    print('city:', city)
enroll('Sarah', 'F')
enroll('Bob', 'M', 7)
enroll('Adam', 'M', city='Tianjin')

def add_end(L=[]): # L is created every time
    L.append('END')
    return L
add_end() # ['END']
add_end() # ['END', 'END']
add_end() # ['END', 'END', 'END']

# corrected:
def add_end(L=None):
    if L is None:
        L = []
    L.append('END')
    return L


################################### '*args' ###################################
def calc(*numbers):  # arg list -> tuple
    sum = 0
    for n in numbers:
        sum = sum + n * n
    return sum
calc(1, 2)
calc(1, 2, 3)
calc()

calc(*nums)  # list/tuple -> arg list


################################## '**kwargs' ##################################
def person(name, age, **kw):  # arg list -> dict
    print('name:', name, 'age:', age, 'other:', kw)
person('Michael', 30) # kw = {}
person('Bob', 35, city='Beijing')
# kw = {'city': 'Beijing'}
person('Adam', 45, gender='M', job='Engineer')
# kw = {'gender': 'M', 'job': 'Engineer'}

extra = {'city': 'Beijing', 'job': 'Engineer'}
person('Jack', 24, **extra)   # dict -> arg list


################################# Named params #################################
def person(name, age, *, city='Beijing', job):
    print(name, age, city, job)
person('Jack', 24, city='Beijing', job='Engineer')
person('Jack', 24, 'Beijing', 'Engineer') # error


############################### Iterator on dict ###############################
d = {'a': 1, 'b': 2, 'c': 3}
for key in d:
    print(key)   # a b c
for value in d.values():
    print(value) # 1 2 3
for k, v in d.items():
    print(k, v)


################################### Iterable ###################################
from collections import Iterable
isinstance('abc', Iterable) # True
isinstance(123, Iterable)   # False


################################ List Generator ################################
[x * x for x in range(1, 11)]
[x * x for x in range(1, 11) if x % 2 == 0]
[m + n for m in 'ABC' for n in 'XYZ']
[k + '=' + v for k, v in d.items()]
L = ['Hello', 'World', 'IBM', 'Apple']
[s.lower() for s in L]


################################## Generator ##################################
(x * x for x in range(10))
next(g) # 0
next(g) # 1
next(g) # 4 ...

G = (x * x for x in range(10))
for n in G:
    print(n)

def fib(max):
    n, a, b = 0, 0, 1
    while n < max:
        yield b
        a, b = b, a + b
        n = n + 1
    return 'done'
object = fib(10) # type = genetator object

def triangles():
    result = [1]
    while True:
        yield result
        a, b = [0] + result, result + [0]
        result = [a[i] + b[i] for i in range(len(a))]


######################### Iterable / Iterator / iter() #########################
isinstance('abc', Iterable)  # True
isinstance('abc', Iterator)  # False
isinstance(iter('abc'), Iterator) # True


############################ Higher-order functions ############################
def add(x, y, f):
    return f(x) + f(y)
add(-5, 6, abs) # = abs(-5) + abs(6) = 11


##################################### map #####################################
it = map(abs, [-1, -2, -3]) # iterator
list(it) # [1, 2, 3]


#################################### reduce ####################################
# reduce(f, [x1, x2, x3, x4]) = f(f(f(x1, x2), x3), x4)
from functools import reduce
def add(x, y):
    return x + y
reduce(add, [1, 3, 5, 7, 9])  # 25

from functools import reduce
def char2num(s):
    return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]
def str2int(s):
    return reduce(lambda x, y: x * 10 + y, map(char2num, s))


#################################### filter ####################################
def is_odd(n):
    return n % 2 == 1
list(filter(is_odd, [1, 2, 4, 5, 6, 9, 10, 15])) # = [1, 5, 9, 15]
# or: for x in filter(..) ....


################################### Sorting ###################################
sorted(['bob', 'about', 'Zoo', 'Credit'])
# ['Credit', 'Zoo', 'about', 'bob']
sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower)
# ['about', 'bob', 'Credit', 'Zoo']
sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower, reverse=True)
# ['Zoo', 'Credit', 'bob', 'about']


############################## Return a function ##############################
def lazy_sum(*args):
    def sum():
        ax = 0
        for n in args:
            ax = ax + n
        return ax
    return sum
f = lazy_sum(1, 3, 5, 7, 9)
f   # function
f() # 25


################################### Closure ###################################
def count():
    def f(j):  # Bind i->j
        def g():
            return j*j
        return g
    fs = []
    for i in range(1, 4):
        fs.append(f(i))
    return fs
f1, f2, f3 = count()


################################## Decorator ##################################
import functools
def log(text):
    def decorator(func):
        @functools.wraps(func) # 把func的name等属性复制给wrapper
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator

@log("call")
def now():
    print('2015-3-25')

now()
# call now():
# 2015-3-25


############################## A Standard Module ##############################

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Michael Liao'

import sys

def test():
    args = sys.argv
    if len(args)==1:
            print('Hello, world!')
    elif len(args)==2:
        print('Hello, %s!' % args[1])
    else:
        print('Too many arguments!')

if __name__=='__main__':
    test()


#################################### Class ####################################
class Student:

    def __init__(self, name, score):
        self.__name = name
        self.__score = score

    def print_score(self):
        print('%s: %s' % (self.__name, self.__score))


################################### Inherit ###################################
class Animal:
    def run(self):
        print('Animal is running...')

class Dog(Animal):
    pass

class Tortoise(Animal):
    def run(self):
        print('Tortoise is running slowly...')

class Runnable:
    def run(self):
        print('Running...')

class Husky(Mammal, Runnable):  # multi
    pass


########################### Some built-in functions ###########################
isinstance(h, Husky)
isinstance(h, (int, float))
dir(object)
getattr(obj, 'attr')
setattr(obj, 'attr', 123)
hasattr(obj, 'attr')

class Student:
    common_attr = 'hello'
    def common_func():
        pass


#################################### Slots ####################################
class Student(object):
    __slots__ = ('name', 'age')


################################### Property ###################################
class Student:

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0 or value > 100:
            raise ValueError('score must between 0 ~ 100!')
        self._score = value

s = Student()
s.score = 60 # OK, -> s.set_score(60)
s.score # OK -> s.get_score() -> 60


######################### Built-in functions of object #########################
__str__(self)
__repr__(self)   # __repr__ = __str__
__iter__(self)  # return an iterator object
__getitem__(self, n_or_slice)  # [n] [n:m]
__getattr__(self, attr_name)
__call__(self)


################################## Enumerate ##################################
enumerate(['A', 'B', 'C'])  # {0:'A', 1:'B', 2:'C'}
for i, value in enumerate(['A', 'B', 'C']):
    print(i, value)

from enum import Enum
Month = Enum('Month', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))
Month.Jan  # == 1. Enum begins from 1
Month['Jan']
Month(1)

for name, member in Month.__members__.items():
    print(name, '=>', member, ',', member.value)


############################ Another usage of enum ############################
from enum import Enum, unique
@unique  # make sure no duplicated values
class Weekday(Enum):
    Sun = 0 # set Sun = 0
    Mon = 1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6


######################## 'try' statement and exception ########################
try:
    print('try...')
    r = 10 / 0
    print('result:', r)
except ZeroDivisionError as e:
    print('except:', e)
else:
    pass
finally:
    print('finally...')
print('END')

class FooError(ValueError):
    pass

raise FooError('invalid value: %s' % s)


################################ logging module ################################
import logging
logging.exception(e)
logging.info('info') # debug, info, warning, error
logging.basicConfig(level=logging.INFO)


############################## 'assert' statement ##############################
assert n != 0, 'n is zero!'
# python -O to shut down asserts


################################## Unit test ##################################
import unittest

from mydict import Dict

class TestDict(unittest.TestCase):

    def test_init(self):
        d = Dict(a=1, b='test')
        self.assertEqual(d.a, 1)
        self.assertEqual(d.b, 'test')
        self.assertTrue(isinstance(d, dict))

    def test_keyerror(self):
        d = Dict()
        with self.assertRaises(KeyError):
            value = d['empty']

    def other_func(self):  # not run
        pass

    def setUp(self):
        print('setUp...')

    def tearDown(self):
        print('tearDown...')

if __name__ == '__main__':
    unittest.main()
# or  python3 -m unittest mydict_test


################################### Doctest ###################################
# `...` for some output
class Dict(dict):
    '''
    Simple dict but also support access as x.y style.

    >>> d1 = Dict()
    >>> d1['x'] = 100
    >>> d1.x
    100
    >>> d1.y = 200
    >>> d1['y']
    200
    >>> d2 = Dict(a=1, b=2, c='3')
    >>> d2.c
    '3'
    >>> d2['empty']
    Traceback (most recent call last):
        ...
    KeyError: 'empty'
    >>> d2.empty
    Traceback (most recent call last):
        ...
    AttributeError: 'Dict' object has no attribute 'empty'
    '''


############################### File Operations ###############################
f = open('/Users/michael/notfound.txt', 'r')
f.read() # read all -> str
f.readline()
f.read(size_in_bytes)
f.readlines() # -> list
f.close()

with open('/path/to/file', 'r') as f:
    for line in f.readlines():
        print(line.strip()) # delelte '\n'
    # close when leaving 'with' block

f = open('/Users/michael/test.jpg', 'rb')
f.read() # -> bytes

f = open('/Users/michael/gbk.txt', 'r', encoding='gbk')
f.read()  # -> str

f = open('/Users/michael/gbk.txt', 'r', encoding='gbk', errors='ignore')

f = open('/Users/michael/test.txt', 'w')
f.write('Hello, world!')
f.close()

with open('/Users/michael/test.txt', 'w') as f:
    f.write('Hello, world!')


################################ String Buffer ################################
from io import StringIO
f.write('hello')
f.write('world!')
print(f.getvalue())

from io import StringIO
f = StringIO('Hello!\nHi!\nGoodbye!')
s = f.readline()


################################# Bytes Buffer #################################
from io import BytesIO
f = BytesIO()
f.write('中文'.encode('utf-8'))
print(f.getvalue())


################################# 'os' module #################################
import os
os.name  # 'nt' for windows, 'posix' for linux/unix
os.environ
os.environ.get('PATH')
os.path.abspath('.')
os.path.join('/Users/michael', 'testdir')
os.mkdir('/Users/michael/testdir')
os.rmdir('/Users/michael/testdir')
os.path.split('/Users/michael/testdir/file.txt')
# ('/Users/michael/testdir', 'file.txt')
os.path.splitext('/path/to/file.txt')
# ('/path/to/file', '.txt')
os.rename('test.txt', 'test.py')
os.remove('test.py')
os.listdir('.')
[x for x in os.listdir('.') if os.path.isfile(x) and os.path.splitext(x)[1]=='.py']


############################### 'pickle' module ###############################
import pickle
d = dict(name='Bob', age=20, score=88)
pickle.dumps(d) # -> bytes
with open('dump.txt', 'wb') as f:
    pickle.dump(d, f)

with open('dump.txt', 'rb') as f:
    d = pickle.load(f)


################################ 'json' module ################################
import json
d = dict(name='Bob', age=20, score=88)
json.dumps(d) # -> str
json_str = '{"age": 20, "score": 88, "name": "Bob"}'
json.loads(json_str) # -> dict
json.load(file)

import json
class Student(object):
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score
    def student2dict(std):
        return {
            'name': std.name,
            'age': std.age,
            'score': std.score
        }
print(json.dumps(s, default=student2dict))

print(json.dumps(s, default=lambda obj: obj.__dict__))

def dict2student(d):
    return Student(d['name'], d['age'], d['score'])
json_str = '{"age": 20, "score": 88, "name": "Bob"}'
json.loads(json_str, object_hook=dict2student))


############################## Regular expression ##############################
import re
re.match(r'^\d{3}\-\d{3,8}$', '010-12345') # Match object or None
re.split(r'\s+', 'a b   c') # ['a', 'b', 'c']
m = re.match(r'^(\d{3})-(\d{3,8})$', '010-12345')
m.group(0) # '010-12345'
m.group(1) # '010'
m.group(2) # '12345'
m.groups() # ('010', '12345')
re_telephone = re.compile(r'^(\d{3})-(\d{3,8})$')
re_telephone.match('010-12345')


################################# Data & Time #################################
from datetime import datetime
now = datetime.now()
print(now) # 2015-05-18 16:28:07.198690
dt = datetime(2015, 4, 19, 12, 20)
print(dt)  # 2015-04-19 12:20:00
dt.timestamp() # 1429417200.0
dt = datetime.fromtimestamp(1429417200.0)
print(dt)  # 2015-04-19 12:20:00
cday = datetime.strptime('2015-6-1 18:19:59', '%Y-%m-%d %H:%M:%S')
cday_str = cday.strftime('%a, %b %d %H:%M')

from datetime import datetime, timedelta
now = datetime.now()
now + timedelta(days=2, hours=12)

from datetime import datetime, timedelta, timezone
datetime.utcnow()
bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))


################################# Named tuple #################################
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
p.x # = 1
p.y # = 2


#################################### deque ####################################
from collections import deque
q = deque(['a', 'b', 'c'])
q.append('x')
q.appendleft('y')
q.pop()
q.popleft()


################################# defaultdict #################################
from collections import defaultdict
dd = defaultdict(lambda: 'N/A')
dd['key1'] = 'abc'
dd['key1']  # = 'abc'
dd['key2']  # = 'N/A'


################################# OrderedDict #################################
from collections import OrderedDict
od = OrderedDict()
od['z'] = 1
od['y'] = 2
od['x'] = 3
list(od.keys()) # ['z', 'y', 'x']


################################### Counter ###################################
from collections import Counter
c = Counter()
for ch in 'programming':
    c[ch] = c[ch] + 1


#################################### base64 ####################################
import base64
base64.b64encode(b'binary\x00string')
# b'YmluYXJ5AHN0cmluZw=='
base64.b64decode(b'YmluYXJ5AHN0cmluZw==')
# b'binary\x00string'
base64.urlsafe_b64encode(b'i\xb7\x1d\xfb\xef\xff')
base64.urlsafe_b64decode('abcd--__')


################################# binary pack #################################
import struct
struct.pack('>I', 10240099) # '>' for big-endian, 'I' for 4-byte int
struct.unpack('>IH', b'\xf0\xf0\xf0\xf0\x80\x80')
# (4042322160, 32896)
struct.unpack('<ccIIIIIIHH', bmp_header)


##################################### Hash #####################################
import hashlib

md5 = hashlib.md5() # or hashlib.sha1()
md5.update('how to use md5 in '.encode('utf-8'))
md5.update('python hashlib?'.encode('utf-8'))
print(md5.hexdigest())


################################## itertools ##################################
import itertools
itertools.count(1)  # 1 2 3 4 5 ...
itertools.cycle('ABC')  # A B C A B ...
itertools.repeat('A')  # A A A A A...
itertools.repeat('A', 3) # A A A [end]

natuals = itertools.count(1)
ns = itertools.takewhile(lambda x: x <= 10, natuals)
list(ns) # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

itertools.chain('ABC', 'XYZ')
itertools.groupby('AAABBBCCAAA') # (key, group)
itertools.groupby('AaaBBbcCAAa', lambda c: c.upper())

A ['A', 'a', 'a']
B ['B', 'B', 'b']
C ['c', 'C']
A ['A', 'A', 'a']


################################ Web operation ################################
from urllib import request

req = request.Request('http://www.douban.com/')
req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
with request.urlopen(req) as f:
    print('Status:', f.status, f.reason)
    for k, v in f.getheaders():
        print('%s: %s' % (k, v))
    print('Data:', f.read().decode('utf-8'))

from urllib import request, parse

print('Login to weibo.cn...')
email = input('Email: ')
passwd = input('Password: ')
login_data = parse.urlencode([
    ('username', email),
    ('password', passwd),
    ('entry', 'mweibo'),
    ('client_id', ''),
    ('savestate', '1'),
    ('ec', ''),
    ('pagerefer', 'https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F')
])

req = request.Request('https://passport.weibo.cn/sso/login')
req.add_header('Origin', 'https://passport.weibo.cn')
req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
req.add_header('Referer', 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F')

with request.urlopen(req, data=login_data.encode('utf-8')) as f:
    print('Status:', f.status, f.reason)
    for k, v in f.getheaders():
        print('%s: %s' % (k, v))
    print('Data:', f.read().decode('utf-8'))


########################## From Iterator to Coroutine ##########################
def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()

c = consumer()
produce(c)


################################## Coroutine ##################################
import asyncio

@asyncio.coroutine
def hello():
    print("Hello world!")
    # call asyncio.sleep(1) asynchronously
    r = yield from asyncio.sleep(1)
    print("Hello again!")

# Get EventLoop
loop = asyncio.get_event_loop()
# Run coroutine
loop.run_until_complete(hello())
loop.close()

# in python 3.5
async def hello():
    print("Hello world!")
    # call asyncio.sleep(1) asynchronously
    r = await asyncio.sleep(1)
    print("Hello again!")