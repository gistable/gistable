#!/usr/bin/env python
import sys

COW = r'''
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
'''
MAX_WIDTH = 39

def header(width):
    """ Line above message body """
    return "\n " + "_" * (width + 2) + "\n"

def footer(width):
    """ Line below message body """
    return " " + "-" * (width + 2)

def format_line(line, width, left, right):
    """ Body line template """
    return "%s %s %s\n" % (left, line.ljust(width), right)

def body(lines, width):
    """ Builds message body with given lines """
    if not lines:
        return ""
    L = len(lines)
    if L == 1:
        return format_line(lines[0], width, '<', '>')
    elif L > 1:
        return (
            format_line(lines[0], width, '/', '\\') +
            "".join(map(lambda l:format_line(l, width, '|', '|'), lines[1:-1])) +
            format_line(lines[-1], width, '\\', '/') )
    else:
        assert False, "Length comparation problem. Unexpected conditions met."

def split_lines(text, maxwidth):
    """ Generator produces wrapped lines from text """
    stack = []
    break_idx = -1
    for c in text:
        if c == ' ':
            # space detected
            if not stack or stack[-1] != ' ':
                # add space if it is not duplicate
                stack.append(' ')
                break_idx = len(stack) - 1
        else:
            # letters are welcome
            stack.append(c)
        if len(stack) > maxwidth:
            # break required
            if break_idx == -1:
                #no spaces in stack, so break long word
                yield "".join(stack[:maxwidth])
                stack = stack[maxwidth:]
            else:
                #break by space
                yield "".join(stack[:break_idx])
                stack = stack[break_idx + 1:]
                break_idx = -1
    # yield rest of string
    yield "".join(stack)
        
def cowsay(text):
    lines = list(split_lines(text, MAX_WIDTH))
    width = max(map(len, lines))
    ob  = header(width)
    ob += body(lines, width)
    ob += footer(width)
    ob += COW
    return ob

if __name__ == '__main__':
    if (sys.version_info > (3, 0)):
        phrase = " ".join(sys.argv[1:])
    else:
        coding = sys.getfilesystemencoding()
        phrase = " ".join(arg.decode(coding) for arg in sys.argv[1:])
    print(cowsay(phrase))
