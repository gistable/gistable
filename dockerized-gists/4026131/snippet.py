import signal, time, traceback, threading

def start(interval=0.1):
    global _interval, _samples
    _samples = []
    signal.signal(signal.SIGALRM,_sample)
    signal.setitimer(signal.ITIMER_REAL,interval,interval)
    
def stop():
    global _samples
    signal.setitimer(signal.ITIMER_REAL,0,0)
    samples, _samples = _samples, []
    samples.append((time.time(),None,None,[]))
    return samples
    
def _sample(signo,frame):
    thread = threading.current_thread()
    row = (time.time(),thread.ident,thread.name,traceback.extract_stack(frame))
    if not _samples or row[1:] != _samples[-1][1:]: # new stack since last sample?
        _samples.append(row)
