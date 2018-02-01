COLOR_CODES = {
    'green': '\033[32m',
    'bgreen': '\033[1;32m',
    'bgrey': '\033[1;30m',
    'reset': '\033[0m'
}

def color(text, color_name):
    return COLOR_CODES[color_name]+text+COLOR_CODES['reset']