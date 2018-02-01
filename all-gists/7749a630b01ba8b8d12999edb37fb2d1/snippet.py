import sys
import traceback


def _format_value(key, value, first_n=20, last_n=20):
    s = repr(value)
    s = s.replace('\n', ' ').strip()
    if len(s) > first_n + last_n + 3:
        s = s[:first_n] + "..." + s[-last_n:]
    return "%s: %s" % (key, s)


def _format_locals(values):
    result = []
    for key, value in values.items():
        result.append(_format_value(key, value))
    return '\n'.join(result)


def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)

    while tb.tb_next:
        tb = tb.tb_next
    print(_format_locals(tb.tb_frame.f_locals))


sys.excepthook = excepthook
