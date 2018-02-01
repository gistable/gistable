from time import sleep
import __builtin__
VISCOSITY = 0.5
def stickify(fn, *args, **kwargs):
    def sticky_fn(*args, **kwargs):
        sleep(VISCOSITY)
        return fn(*args, **kwargs)
    return sticky_fn

for k, v in __builtin__.__dict__.iteritems():
    __builtin__.__dict__[k] = stickify(v)
