#!/usr/bin/env python3

import collections
import sys


def rindex(l, e):
    return len(l) - 1 - l[::-1].index(e)


def cut(n):
    print("cut #{}".format(n + 1))
    sys.exit(0)


_serial_number = None


def serial_number():
    global _serial_number

    if _serial_number is None:
        _serial_number = input("serial number: ")
    return _serial_number


def last_digit_odd():
    for char in reversed(serial_number()):
        if '0' <= char <= '9':
            return int(char) % 2 == 1

    sys.exit("you screwed up the serial number")


def main():
    colors = input("colors: ").split()
    counts = collections.Counter(colors)

    if len(colors) == 3:
        if counts['red'] == 0: cut(1)
        if colors[-1] == 'white': cut(2)
        if counts['blue'] > 1: cut(rindex(colors, 'blue'))
        cut(3)

    if len(colors) == 4:
        if counts['red'] > 1 and last_digit_odd(): cut(rindex(colors, 'red'))
        if colors[-1] == 'yellow' and counts['red'] == 0: cut(0)
        if counts['blue'] == 1: cut(0)
        if counts['yellow'] > 1: cut(3)
        cut(1)

    if len(colors) == 5:
        if colors[-1] == 'black' and last_digit_odd(): cut(3)
        if counts['red'] == 1 and counts['yellow'] > 1: cut(0)
        if counts['black'] == 0: cut(1)
        cut(0)

    if len(colors) == 6:
        if counts['yellow'] == 0 and last_digit_odd(): cut(2)
        if counts['yellow'] == 1 and counts['white'] > 1: cut(3)
        if counts['red'] == 0: cut(5)
        cut(3)

    sys.exit("you screwed up the number of colors")


if __name__ == '__main__':
    main()
