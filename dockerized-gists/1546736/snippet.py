#!/usr/bin/env python
# coding: utf-8

"""
String to Brainfuck.

Converts a string to a brainfuck code that prints that string.

Author: j0hn <j0hn.com.ar@gmail.com>
"""

import sys


def char2bf(char):
    """Convert a char to brainfuck code that prints that char."""

    result_code = ""
    ascii_value = ord(char)
    factor = ascii_value / 10
    remaining = ascii_value % 10

    result_code += "%s\n" % ("+" * 10)
    result_code += "[\n"
    result_code += "  >\n"
    result_code += "  %s\n" % ("+" * factor)
    result_code += "  <\n"
    result_code += "  -\n"
    result_code += "]\n"
    result_code += ">\n"
    result_code += "%s\n" % ("+" * remaining)
    result_code += ".\n"
    result_code += "[-]\n"

    return result_code


def str2bf(string):
    """Convert a string to brainfuck code that prints that string."""

    result = ""
    for char in string:
        result += char2bf(char)

    return result


def print_help():
    """Print the help message."""
    message = "python %s: missing arguments\n\n" % sys.argv[0]
    message += "Usage: %s [OPTIONS] STRING\n" % sys.argv[0]
    message += "Options:\n"
    message += "  -h, --help          displays this help message.\n"
    message += "  -s, --small         prints the code in one liner.\n"
    message += "  -n, --newline       adds a new line character "
    message += "at the end of the string.\n"
    sys.stderr.write(message)


def main():
    """Reads the arguments from stdin and outputs the code."""

    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    add_new_line = False
    small_output = False

    if "-n" in sys.argv or "--newline" in sys.argv:
        add_new_line = True

        try:
            sys.argv.remove("-n")
        except ValueError:
            sys.argv.remove("--newline")

    if "-s" in sys.argv or "--small" in sys.argv:
        small_output = True

        try:
            sys.argv.remove("-s")
        except ValueError:
            sys.argv.remove("--small")

    if "-h" in sys.argv or "--help" in sys.argv:
        print_help()
        sys.exit(0)

    input_string = " ".join(sys.argv[1:])

    result = str2bf(input_string + ("\n" * add_new_line))
    if small_output:
        result = result.replace(" ", "").replace("\n", "")

    print result


if __name__ == "__main__":
    main()