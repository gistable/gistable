import functools,threading

def wrap_loop_thread(__sec_interval):
    def recieve_func(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            func(*args,**kwargs)
            thread_loop=threading.Timer(__sec_interval,functools.partial(wrapper,*args,**kwargs))
            thread_loop.start()
        return wrapper
    return recieve_func

INTERVAL_SEC_LOOP=2
@wrap_loop_thread(INTERVAL_SEC_LOOP)
def func_loop(text):
    print(text)

if __name__=="__main__":
    func_loop("hoge")
