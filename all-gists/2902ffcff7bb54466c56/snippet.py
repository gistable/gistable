import sys
import datetime


class logger(object):
    instance = None

    def __init__(self, tag):
        self.tag = str(tag)

    def prn(self, msg, prefix='> ', endl='\n', args=[]):
        msg = '%s [%s][%s] %s%s' % (
            prefix, datetime.datetime.now().strftime('%H:%M:%S'), self.tag, msg, endl)
        msg = msg.format(*args,
                         W='\033[97m',  # white
                         R='\033[91m',  # lt red
                         Y='\033[93m',  # lt yellow
                         G='\033[92m',  # lt green
                         C='\033[96m',  # lt cyan
                         B='\033[94m',  # lt blue
                         P='\033[95m',  # lt purple
                         D='\033[37m',  # lt gray
                         d='\033[90m',  # gray
                         r='\033[31m',  # red
                         y='\033[33m',  # yellow
                         g='\033[32m',  # green
                         c='\033[36m',  # cyan
                         b='\033[34m',  # blue
                         p='\033[35m')  # purple

        sys.stdout.write(msg)
        sys.stdout.flush()

    def nfo(self, msg, endl='\n', args=[]):
        self.prn(msg,
                 prefix='{c}# ',
                 endl=endl,
                 args=args)

    def wrn(self, msg, endl='\n', args=[]):
        self.prn(msg,
                 prefix='{y}* ',
                 endl=endl,
                 args=args)

    def err(self, msg, endl='\n', args=[]):
        self.prn(msg,
                 prefix='{r}! ',
                 endl=endl,
                 args=args)

    def dbg(self, msg, endl='\n', args=[]):
        self.prn(msg,
                 prefix='{d}# ',
                 endl=endl,
                 args=args)

    def fatal(self, msg, endl='\n', args=[]):
        self.prn(msg,
                 prefix='{R}! ',
                 endl=endl,
                 args=args)
        raise Exception(msg)

    def checker(self, msg, checker, args=[]):
        res = ' ... {g}SUCCESS' if checker else' ... {r}FAILED'
        self.nfo(msg + res, args=args)

    def progress(self, it, prefix='', size=60):
        count = len(it)

        def _show(_i):
            x = int(size * _i / count)
            sys.stdout.write("%s[%s%s] %i/%i\r" %
                             (prefix, "#" * x, "." * (size - x), _i, count))
            sys.stdout.flush()
        _show(0)
        for i, item in enumerate(it):
            yield item
            _show(i + 1)
        sys.stdout.write("\n")
        sys.stdout.flush()


def get(tag):
    return logger(tag)

# test

if __name__ == '__main__':
    import time
    log = get('LOG')
    log.prn(
        '{r}RED {p} PURPLE {y} YELLOW {g} GREEN {c} CYAN {b} BLUE {d} DARK ')
    log.prn(
        '{R}RED {P} PURPLE {Y} YELLOW {G} GREEN {C} CYAN {B} BLUE {D} DARK ')

    log.dbg('It is debug {g}message')
    log.nfo('It is info  {y}message')
    log.wrn('It is warn  {b}message')
    log.err('It is error {c}message')

    for x in xrange(10):
        log.checker('pass: {B}{0}', (x > 5), args=[x])

    for i in log.progress(range(15), "progress test: ", 80):
        time.sleep(0.4)

#   log.fatal('fatal problem!')
