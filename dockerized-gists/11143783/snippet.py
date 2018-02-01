#!/usr/bin/env python

import sys
import socket
import subprocess
import time
import argparse


def morse(s):
	code = '_etianmsurwdkgohvf_l_pjbxcyzq__54_3___2__+____16=/_____7___8_90'

	def e(l):
		i = code.find(l)
		v = ''
		while i > 0:
			v = '-.'[i % 2] + v
			i = (i - 1) // 2
		return v or '/'
	return map(e, s)


def _blink(t):
	subprocess.call(['echo 1 > /sys/class/leds/led0/brightness'], shell=True)
	time.sleep(t)
	subprocess.call(['echo 0 > /sys/class/leds/led0/brightness'], shell=True)


def dot(t):
	_blink(t)


def dash(t):
	_blink(t * 3)


def pause(t):
	time.sleep(t * 3)


def main():
	parser = argparse.ArgumentParser(
		description='Output stdin to raspberry led0 in morse')
	parser.add_argument('text', nargs='?', help='text to output')
	parser.add_argument(
		'-u', '--unit',
		type=float, default=0.2,
		help='time unit in seconds')
	parser.add_argument(
		'-i', '--ip',
		action='store_true', default=False,
		help='output local ip address')
	parser.add_argument(
		'-b', '--bin',
		action='store_true', default=False,
		help='output using binary encoding')
	args = parser.parse_args()

	if args.text:
		text = args.text
	elif not sys.stdin.isatty():
		text = sys.stdin.read()
	elif args.ip:
		text = socket.gethostbyname(socket.getfqdn())
	else:
		parser.error('the following arguments are required: text')

	if args.bin:
		data = (bin(i)[2::] for i in str.encode(text))
		conv = binary_conv
	else:
		data = morse(text)
		conv = morse_conv

	for i in data:
		for k in i:
			conv[k](args.unit)
		time.sleep(args.unit)

morse_conv = {'.': dot, '-': dash, '/': pause}
binary_conv = {'0': dot, '1': dash}

if __name__ == '__main__':
	main()
