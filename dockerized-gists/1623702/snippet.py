import logging
import random
import re


class DelegatingHandler(logging.Handler):
    def __init__(self, *handlers):
        logging.Handler.__init__(self)
        self.handlers = handlers
    
    def handle(self, record):
        rv = self.filter(record)
        if rv:
            for h in self.handlers:
                h.handle(record)
        return rv

if __name__ == '__main__':
    class NumberFilter(logging.Filter):
        def __init__(self):
            self.pattern = re.compile('^\d+$')
 
        def filter(self, record):
            return self.pattern.match(record.msg)

    class OddFilter(NumberFilter):
        def filter(self, record):
            return (int(record.msg) % 2) == 1
        
    class EvenFilter(NumberFilter):
        def filter(self, record):
            return (int(record.msg) % 2) == 0


    root = logging.getLogger()
    h1 = logging.FileHandler('odd.log', 'w')
    h1.addFilter(OddFilter())
    h2 = logging.FileHandler('even.log', 'w')
    h2.addFilter(EvenFilter())
    h = DelegatingHandler(h1, h2)
    h.addFilter(NumberFilter())
    root.addHandler(h)
    for i in range(10000):
        if random.choice([True, False]):
            msg = str(random.randint(0, 100))
        else:
            msg = random.choice(['one', 'two', 'three'])
        root.warning(msg)
