# Copyright David Kendal, 2013
# You may redistribute this code, modified or unmodified, provided that this article is preserved in its entirety.
# Like all software, and information generally, this work is without warranty.

import inspect

# "if isscript():" is "if __name__ is '__main__':"
def isscript(frames=1):
    callers = inspect.getouterframes(inspect.currentframe())
    return callers[frames][0].f_globals['__name__'] == '__main__'

# "@script" / "def main():" is "if __name__ is '__main__':"
def script(main):
    if isscript(2):
        return main()

# "@noscript" / "def main():" is "if __name__ != '__main__':"
def noscript(main):
    if not isscript(2):
        return main()
