from functools import wraps


def mydecorator(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        print ("Before decorated function <" + func.__name__ +">")
        r = func(*args, **kwargs)
        print ("After decorated function <" + func.__name__ +">")
        return r
    return func_wrapper


@mydecorator
def myfunc(myarg):
    print("executing <myfunc> with arg: <" + str(myarg) + "> ...")
    return "returned value from myfunc"


def main():
    """
    
    """
    r = myfunc('asdf')
    print("result from <myfunc>: <" + r + ">")
    
    
if __name__ == '__main__':
    main()