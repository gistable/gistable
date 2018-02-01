import __main__
import os

_ansi_color_codes = {
    "black":30,
    "red":31,
    "green":32,
    "yellow":33,
    "blue":34,
    "magenta":35,
    "cyan":36,
    "white":37,
}

_ansi_color_format = "\033[%d;%dm"
_ansi_color_reset = "\033[0m"
 
####################
# Public Functions #
####################

def colorise(text, color, bold):
    if _supports_ansi_codes() and color in _ansi_color_codes:
        ansi_color_string = _ansi_color_format % ((1 if bold else 0), _ansi_color_codes[color])
        return ansi_color_string + text + _ansi_color_reset
    else:
        return text
 
def error(msg):
    print _script_string_color("Error: " + msg, "red", 1)
 
def warning(msg):
    print _script_string_color("Warning: " + msg, "yellow", 1)
 
def message(msg):
    print _script_string_color(msg[0].upper() + msg[1:], "white", 1)

def error_string(msg):
    return _script_string_color("Error: " + msg, "red", 1)
 
def warning_string(msg):
    return _script_string_color("Warning: " + msg, "yellow", 1)
 
def message_string(msg):
    return _script_string_color(msg[0].upper() + msg[1:], "white", 1)
 
def file_exists(filename):
    try:
        with open(filename) as f:
            return True
    except IOError as e:
        return False

#####################
# Private Functions #
#####################

def _supports_ansi_codes():
    return os.name != "nt"

def _top_level_script_name():
    # import inspect
    # print inspect.stack()[-1][1]
    return os.path.basename(__main__.__file__)

def _script_string_color(msg, color, bold):
    full_msg = colorise("[%s]", color, bold) + " %s"
    return full_msg % (_top_level_script_name(), msg)