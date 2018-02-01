import time, functools

def timeit(func): 
    @functools.wraps(func) 
    def __do__(*args,**kwargs): 
        start = time.time() 
        result= func(*args,**kwargs) 
        print '%s used time %ss'%(func.__name__,time.time()-start) 
        return result 
    return __do__ 