# encoding: utf8

# 什么是lambda函数？它有什么好处？另外python在函数式编程方面提供了些什么函数和语法？
# - lambda 就是匿名函数
# - 好处: 可以动态生成一个函数对象，不用给这个对象命名，污染名字空间
# - 函数：map()/filter()
# - 语法：可以函数内部定义函数，闭包支持

# 详细说说tuple、list、dict的用法，它们的特点；
# - tuple 固定长度的子项不可变的顺序型容器，一般用来做常量(策划配表)或者表示少量属性的对象(比如pos)表示
# - list 可变长度的子项可变的顺序型容器，一般用来实现队列/栈之类只需要用数字索引/分片分段访问的容器
# - dict 可变长度的hash字典容器，key是多种类型

# 说说python中装饰器、迭代器的用法；描述下dict 的 items() 方法与 iteritems() 方法的不同；
# - 装饰器通常就是说以函数对象作为参数的，内部定义一个新函数包装参数函数，并返回这个新函数的函数
#   装饰器可以包装函数，再函数调用前后做某些工作，甚至替换函数实现
#   比如下面就是一个装饰器，会包装已有的函数，每次调用是做打印
#   def trace(func):
#       def f(*args, **kw):
#           print "call %s %s %s" % (func, args, kw)
#           return func(*args, **kw)
#       return f

#   @trace
#   def afunc(): pass

#   python提供@语法，等同于：
#   def afunc(): pas
#   afunc = trace(afunc)

# - 迭代器是指遵循迭代器协议的对象，这类对象在被for循环时，每次迭代生成下一个项，不用一开始就生成整个列表
# - items()返回[(key,value)]的列表对象，iteritems()返回迭代器对象，iteritems()循环时不可以增删dict的内容

# 知道greenlet、stackless吗？说说你对线程、协程、进程的理解；
# - greenlet是一个python c lib，提供python的协程支持，gevent就是基于greenlet的
# - stackless，没仔细过，刚粗略看以下，是一个增强版本的python解释器
#   提供内建的协程支持，围绕协程提供Microthreads/Channels/Scheduling/Serialisation的支持
# - 进程也就是一个程序执行时的状态
# - 线程由进程内创建，进程可以通过创建多个线程来更好的利用多核心的机器
#   每个线程一个执行流，线程的调度由OS负责，程序员不能控
#   多线程程序在编写要注意内存中跨线程共享的数据的读写加速
# - 协程是线程内的概念，一个线程可以通过保存调用栈和恢复调用栈来复用线程的执行流，提供多个执行流的抽象
#   每个协程为单独一个执行流，调度由程序员来控制
#   像gevent就通过把阻塞io接口的写法用协程包装起来，自动调度，提供一种用同步代码的方式写出执行上实际是异步的程序

# 讲讲对unicode, gbk, utf-8等的理解，python2.x是如何处理编码问题？

# - unicode/gbk/utf8都是文本编码方案
# - python2.x 可以通过str.decode/str.encode处理字符串的文本编码

string_of_utf8 = "终端"
string_of_unicode = u"终端"
string_of_unicode2 = string_of_utf8.decode("utf8")
string_of_gbk = string_of_unicode2.encode("gbk")

for k, v in globals().items():
    if k.startswith("string_of"):
        print k, v

# Python是如何进行内存管理的？python的程序会内存泄露吗？说说有没有什么方面防止或检测内存泄露？ 
# - 内存管理：具体看各种内存池管理，intern机制看Python源码解析一书，没记不住...
#   每个python对象都是有引用计数的，引用计数一旦为0，虚拟机自动释放对象，回收内存
#   虚拟机提供一个处理循环引用导致无法通过引用技术为0的自动垃圾回收机制
# - Python也会内存泄露，Python本身的垃圾回收机制无法回收重写了__del__的循环引用的对象
# - 程序员管理好每个python对象的引用，尽量在不需要使用对象的时候，断开所有引用
#   尽量少通过循环引用组织数据，可以改用weakref做弱引用或者用id之类的句柄访问对象
#   通过gc模块的接口可以检查出每次垃圾回收有哪些对象不能自动处理，再逐个逐个处理

# 关于python程序的运行性能方面，有什么手段能提升性能？
# - cpu：
#   写C lib或Cython，将python的运算转移到C层去做
#   改用PyPy类JIT解释器提高解释器性能
#   使用多进程组织python程序，充分利用机器多个核心
# - network io：
#   使用nonblock io，不使用block io，避免io操作阻塞当前执行流
#   采用异步写法，比如使用Twisted
#   采用同步写法，比如使用gevent
 
# list对象 alist [{'name':'a','age':20},{'name':'b','age':30},{'name':'c','age':25}]，请按alist中元素的 age 由大到小排序；
alist = [{'name':'a','age':20},{'name':'b','age':30},{'name':'c','age':25}]
alist.sort(key = lambda x: -x["age"])
print alist

# 两个list对象 alist ['a','b','c','d','e','f'], blist ['x','y','z','d','e','f']，请用简洁的方法合并这两个list，并且list里面的元素不能重复；
def merge_list(*args):
    s = set()
    for l in args:
        s = s.union(l)
    return list(s)

alist = ['a','b','c','d','e','f']
blist = ['x','y','z','d','e','f']

mlist = merge_list(alist, blist)
assert mlist and all(mlist.count(e) == 1 for e in mlist)
 
# 打乱一个排好序的 list 对象 alist；
from random import shuffle
alist = range(10)
shuffle(alist)
print "shuffle", alist

# 简单实现一个stack；
class Stack:

    def __init__(self):
        self.values = []

    def push(self, o):
        self.values.append(o)

    def pop(self):
        return self.values.pop()

s = Stack()
s.push(1)
s.push(2)
assert s.pop() == 2
assert s.pop() == 1
s.push(3)
s.push(4)
assert s.pop() == 4
assert s.pop() == 3
 
# 输入某年某月某日，判断这一天是这一年的第几天？(可以用python标准库)
from datetime import datetime
def day_of_year(year, month, day):
    return (datetime(year, month, day) - datetime(year, 1, 1)).days + 1

assert day_of_year(2014, 1, 10) == 10
 
# 将字符串："k:1|k1:2|k2:3|k3:4"，处理成python字典：{k:1, k1:2, ... }
def string_to_dict(string):
    d = {}
    for kv in string.split("|"):
        k, v = kv.split(":")
        if v.isdigit(): 
            v = int(v)
        d[k] = v
    return d

string = "k:1|k1:2|k2:3|k3:4"
print string_to_dict(string)
string2 = "k:1"
print string_to_dict(string2)
