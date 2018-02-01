class Timer(object):
    def __init__(self, name):
        print("%s: " % name, end="")
    def __enter__(self):
        self.t0 = time.time()
    def __exit__(self, *args):   
        print("%.3fs" % (time.time() - self.t0))

with Timer("XXX"):
    call_function()