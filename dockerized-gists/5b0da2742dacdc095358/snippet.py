#!/usr/bin/env python
#_*_ conding:utf8 _*_

def log(string): 

    if  isinstance(string,str):

        def decorator(func):

            def wrapper(*args,**kw):

                print '%s %s' %(string,func.__name__)

                return func(*args,**kw)

            return wrapper

        return decorator

    else:

        def wrapper(*args,**kw):

            print '%s' %string.__name__

            return string(*args,**kw)
        return wrapper
        
        
        
        


@log
def f1():
    pass


@log('excute')
def f2():
    pass

f1()
f2()





"""
--------------------------------------------------
Result:

    [root@njrd117 tools]# ./decorator.py 
    f1
    excute f2
--------------------------------------------------
"""
