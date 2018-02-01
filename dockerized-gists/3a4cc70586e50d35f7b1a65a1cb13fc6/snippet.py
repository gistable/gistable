class ExponentialBackoff(object):
    '''
    Simple iterator that calculates exponential backoff durations
    '''
    def __init__(self, *args, **kwargs):
        self.initial_interval = kwargs.pop('initial_interval', 5)
        self.max_interval = kwargs.pop('max_interval', 60)
        self.randomization_factor = kwargs.pop('randomization_factor', 0.5)
        self.multiplier = kwargs.pop('multiplier', 1.5)
        self.max_elapsed_time = kwargs.pop('max_elapsed_time', 900)

        self.started = time.time()
        self.interval = self.initial_interval

    def _elapsed(self):
        return time.time() - self.started

    def _should_stop(self):
        return self.max_elapsed_time and self._elapsed() > self.max_elapsed_time

    def _next_interval(self):
        result = self.interval * self.multiplier
        return min(result, self.max_interval) if self.max_interval else result

    def _select_from_interval(self):
        delta = self.randomization_factor * self.interval
        low, high = self.interval - delta, self.interval + delta
        return random.uniform(low, high)

    def __iter__(self):
        return self

    def next(self):
        if self._should_stop():
            raise StopIteration

        result = self._select_from_interval()
        self.interval = self._next_interval()
        return result