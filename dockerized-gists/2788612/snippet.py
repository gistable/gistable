from docopt import docopt
import sys

class command(object):
    registry = {}
    short_docs = []
    def __init__(self, doc = None):
        self.short_docs.append(doc)

    def __call__(self, fn):
        command.registry[fn.func_name] = fn
        return fn

    @classmethod
    def dispatch(self, args=sys.argv[1:]):
        func_name = len(args) and args[0] or None
        if func_name is None or not func_name in command.registry:
            sys.stderr.write("Available sub-commands:\n")
            for fn, short_doc in zip(command.registry, command.short_docs):
                sys.stderr.write("\t" + fn + ((" : " + short_doc) if short_doc else "") + "\n")
            sys.exit(1)
        else:
            func = command.registry[func_name]
            arguments = docopt(func.__doc__, args[1:])
            print arguments
            func(**arguments)


@command("do the first thing")
def cmd_a(a, b, c, dnum=22):
    """
    Usage t.py cmd_a [options] arguments
    Options:
      --dnum NUMBER    number of things [default: 24]

    Args:
    a b c
    """
    print dnum + 33
    print a, b, c, dnum


@command("do the other thing")
def cmd_b(a, b, other=None):
    """
    Usage t.py cmd_b [options] arguments
    Options:
    --other             something else

    Args:
    a b
    """
    print a, b, other


if __name__ == '__main__':

    command.dispatch()