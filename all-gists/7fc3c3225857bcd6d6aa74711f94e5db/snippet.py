#!/usr/bin/env python3

# Made by SopaXorzTaker, with additions from nucular
# Use xterm with a black background for the best effect.

import time
import copy
import random

import os, sys
import shlex
import struct
import platform
import subprocess


def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)      # default value
    return tuple_xy
def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass
def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass
def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])


COLORS = [
	"\x1b[30m\u2591",
	"\x1b[31m\u2591",
	"\x1b[32m\u2591",
	"\x1b[33m\u2591",
	"\x1b[34m\u2591",
	"\x1b[35m\u2591",
	"\x1b[36m\u2591",
	"\x1b[37m\u2591",
	"\x1b[38m\u2591",
	"\x1b[39m\u2591",

        "\x1b[47m\x1b[30m\u2592\x1b[0m",
        "\x1b[31m\u2592",
        "\x1b[32m\u2592",
        "\x1b[33m\u2592",
        "\x1b[34m\u2592",
        "\x1b[35m\u2592",
        "\x1b[36m\u2592",
        "\x1b[37m\u2592",
        "\x1b[38m\u2592",
        "\x1b[39m\u2592",

        "\x1b[47m\x1b[30m\u2593\x1b[0m",
        "\x1b[31m\u2593",
        "\x1b[32m\u2593",
        "\x1b[33m\u2593",
        "\x1b[34m\u2593",
        "\x1b[35m\u2593",
        "\x1b[36m\u2593",
        "\x1b[37m\u2593",
        "\x1b[38m\u2593",
        "\x1b[39m\u2593",

        "\x1b[47m\x1b[30m\u2588\x1b[0m",
        "\x1b[31m\u2588",
        "\x1b[32m\u2588",
        "\x1b[33m\u2588",
        "\x1b[34m\u2588",
        "\x1b[35m\u2588",
        "\x1b[36m\u2588",
        "\x1b[37m\u2588",
        "\x1b[38m\u2588",
        "\x1b[39m\u2588",
]

def dissipate(matrix, width, height, coefficient=1.0):
	out_matrix = copy.deepcopy(matrix)

	for y in range(height):
		for x in range(width):
			surround = 0.0

			for y2 in range(y-1, y+2):
				for x2 in range(x-1, x+2):
					index = y2*width + x2
					if x2 in range(width) and y2 in range(height):
						surround += matrix[index]

			index = y*width + x
			out_matrix[index] = surround/9.0*coefficient

	return out_matrix

WIDTH, HEIGHT = get_terminal_size()
WIDTH -= 1
HEIGHT -= 1

matrix = []

for i in range(WIDTH*HEIGHT):
	matrix.append(random.uniform(0.0, 1.0))

while True:
	for y in range(HEIGHT):
		for x in range(WIDTH):
			print(COLORS[min(int(matrix[y*WIDTH + x]*len(COLORS)), len(COLORS)-1)], end="")
			if random.random() > 0.99:
				matrix[y*WIDTH + x] += random.random()*5.0
		print()


	matrix = dissipate(matrix, WIDTH, HEIGHT, random.uniform(0.5, 1.0))
	# If the terminal glitches, try uncommenting the line below and adjusting the value.
	#time.sleep(0.05)
	print("\x1b[2J\x1b[;H", end="")
