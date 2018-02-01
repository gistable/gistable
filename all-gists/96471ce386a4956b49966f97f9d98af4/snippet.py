#!/usr/bin/env python
# Copyright (c) 2017, Brandan Geise [coldfusion]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
import re
import os.path


def main():
	parser = argparse.ArgumentParser(description='Retrieve the NTLM hash from a captured NetNTLMv1 or MSCHAPv2 session')
	parser.add_argument('-H', '--hash', help='File or single NetNTLMv1 or MSCHAPv2 hash', required=False)
	parser.add_argument('-o', '--outfile', help='Outfile file for Hashcat', default='des_keys.txt')
	parser.add_argument('--ct1', help='Hashcat output for decrypted CT1 DES key', required=False)
	parser.add_argument('--ct2', help='Hashcat output for decrypted CT2 DES key', required=False)
	args = parser.parse_args()

	if args.hash:
		if os.path.isfile(args.hash):
			f = open(args.hash, 'r')
			for line in f:
				try:
					parse_hash(line.rstrip(), args.outfile)
				except Exception as error:
					continue
		else:
			parse_hash(args.hash, args.outfile)

		print("hashcat -m 14000 {0} -o {1}.out -a 3 -1 charsets/DES_full.charset --hex-charset ?1?1?1?1?1?1?1?1 -w 3\n".format(args.outfile, (args.outfile).split('.')[0]))

	elif args.ct1 and args.ct2:
		ntlm1 = des_decode(args.ct1)
		ntlm2 = des_decode(args.ct2)
		print("{0}{1}".format(ntlm1, ntlm2))

	else:
		print_error("You must supply either '--hash' or '--ct1' and '--ct2")


def parse_hash(hstring, outfile):
	challenge_regex = re.search('[:$]{1}([\d\w]{16})[:$]?', hstring)
	response_regex = re.search('[:$]{1}([\d\w]{48})[:$]?', hstring)
	if challenge_regex and response_regex:
		challenge = challenge_regex.group(1).lower()
		response = response_regex.group(1).lower()

		# Parse keys
		ct1 = response[0:16]
		ct2 = response[16:32]

		des_key1 = "{0}:{1}".format(ct1, challenge)
		des_key2 = "{0}:{1}".format(ct2, challenge)

		f = open(outfile, 'a')
		f.write("{0}\n".format(des_key1))
		f.write("{0}\n".format(des_key2))

		print_good("CT1 key: {0}".format(des_key1))
		print_good("CT2 key: {0}\n".format(des_key2))


def des_decode(dkey):
	des_keys = map(ord, dkey.decode('hex'))

	ntlm = hex(((des_keys[0] << 0) & ~0x01 | des_keys[1] >> 7) & 0xff)[2:]
	ntlm += hex(((des_keys[1] << 1) & ~0x03 | des_keys[2] >> 6) & 0xff)[2:]
	ntlm += hex(((des_keys[2] << 2) & ~0x07 | des_keys[3] >> 5) & 0xff)[2:]
	ntlm += hex(((des_keys[3] << 3) & ~0x0f | des_keys[4] >> 4) & 0xff)[2:]
	ntlm += hex(((des_keys[4] << 4) & ~0x1f | des_keys[5] >> 3) & 0xff)[2:]
	ntlm += hex(((des_keys[5] << 5) & ~0x3f | des_keys[6] >> 2) & 0xff)[2:]
	ntlm += hex(((des_keys[6] << 6) & ~0x7f | des_keys[7] >> 1) & 0xff)[2:]

	return ntlm


def print_error(msg):
	print("\033[1m\033[31m[-]\033[0m {0}".format(msg))


def print_status(msg):
	print("\033[1m\033[34m[*]\033[0m {0}".format(msg))


def print_good(msg):
	print("\033[1m\033[32m[+]\033[0m {0}".format(msg))


def print_warn(msg):
	print("\033[1m\033[33m[!]\033[0m {0}".format(msg))

if __name__ == '__main__':
	main()
