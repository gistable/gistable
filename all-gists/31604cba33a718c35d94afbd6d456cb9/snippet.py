import time
# Simple Timer
class Timer:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._start = time.time()
    
    def elapsed(self): # elapsed time in seconds (float)
        return time.time() - self._start