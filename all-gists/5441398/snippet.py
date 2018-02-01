import cProfile
 
 
def profile_this(fn):
    def profiled_fn(*args, **kwargs):
        # name for profile dump
        fpath = fn.__name__ + '.profile'
        prof = cProfile.Profile()
        ret = prof.runcall(fn, *args, **kwargs)
        prof.dump_stats(fpath)
        return ret
    return profiled_fn