    def profile_func(filename=None):
        def proffunc(f):
            def profiled_func(*args, **kwargs):
                import cProfile
                import logging
                logging.info('Profiling function %s' % (f.__name__))
                try:
                    profiler = cProfile.Profile()
                    retval = profiler.runcall(f, *args, **kwargs)
                    profiler.dump_stats(filename or '%s_func.profile' % (f.__name__))
                except IOError:
                    logging.exception(_("Could not open profile file '%(filename)s'") % {"filename": filename})

                return retval
            return profiled_func
        return proffunc
