BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7


def colorize(text, fg=None):
    """Prints some text with color."""
    _fg = fg or 0
    return "\033[9%sm%s\033[0m" % (_fg, text)