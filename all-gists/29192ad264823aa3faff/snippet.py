import sys
import os
import linecache

class Profiler:

    def __init__(self, instrument):
        self.instrument = instrument

    def run(self, func, *args, **kwargs):
        self.last_measure = self.instrument()
        self.last_code = None
        self.traces = {}
        oldtrace = sys.gettrace()
        sys.settrace(self.trace)
        result = func(*args, **kwargs)
        sys.settrace(oldtrace)
        self.profile()
        return result

    def trace(self, frame, event, arg):
        if event in ('line', 'call'):
            lineno = frame.f_lineno
            fname = frame.f_globals.get('__file__')
            self.profile((fname, lineno))
        return self.trace

    def profile(self, code=None):
        measure = self.instrument()
        if self.last_code is not None:
            delta = measure - self.last_measure
            trace = self.traces.get(self.last_code, [])
            trace.append(delta)
            self.traces[self.last_code] = trace
        self.last_measure = measure
        self.last_code = code

    def pprint(self):
        print("count\ttime\tfile:line\t\tsource")
        for code in sorted(self.traces):
            fname, lineno = code
            bname = os.path.basename(fname)
            line = linecache.getline(fname, lineno).rstrip()
            while line.lstrip().startswith("@"):
                lineno += 1
                line = linecache.getline(fname, lineno).rstrip()
            trace = self.traces[code]
            count = len(trace)
            total_time = sum(trace)
            fmt = "{}\t{:.2f}\t{}:{}\t{}"
            print(fmt.format(count, total_time, bname, lineno, line))

def profile(prof):
    def decorator(func):
        def wrapper(*args, **kwargs):
            prof.last_measure = prof.instrument()
            prof.last_code = None
            if not hasattr(prof, "traces"):
                prof.traces = {}
            oldtrace = sys.gettrace()
            sys.settrace(prof.trace)
            result = func(*args, **kwargs)
            sys.settrace(oldtrace)
            prof.profile()
            return result
        return wrapper
    return decorator

if __name__ == "__main__":
    import time
    def example(r):
        for i in range(r):
            time.sleep(0.5)
    prof = Profiler(time.time)
    prof.run(example, 4)
    prof.pprint()
