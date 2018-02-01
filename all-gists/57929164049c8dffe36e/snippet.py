import cProfile

def with_profile(fn):
    def _profile_fn(*args, **kwargs):
        prof = cProfile.Profile()
        ret = prof.runcall(fn, *args, **kwargs)
        print "profile for:", fn.__name__
        prof.print_stats()
        return ret
    return _profile_fn