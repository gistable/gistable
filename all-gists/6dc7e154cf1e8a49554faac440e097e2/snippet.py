import threading

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

# example
a = 1 
def inc_a():
    global a
    a += 1
    
set_interval(inc_a,1)