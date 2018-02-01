class LossyCounting(object):
    '''
    Implements the "lossy counting" algorithm from
    "Approximate Frequency Counts over Data Streams" by Manku & Motwani
    
    Experimentally run-time is between 1-3 microseconds on core i7
    '''
    def __init__(self, epsilon=0.001):
        self.n = 0
        self.d = {}  # {key : (count, error)}
        self.b_current = 1
        self.w = int(1 / epsilon)

    def add(self, data):
        self.n += 1
        if data in self.d:
            self.d[data][0] += 1
        else:
            self.d[data] = [1, self.b_current - 1]

        if self.n % self.w == 0:
            self.d = dict([(k, v) for k, v in self.d.items()
                           if sum(v) > self.b_current])
            self.b_current += 1

