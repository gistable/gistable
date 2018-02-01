#!/usr/bin/python

#Feed the decompiled Tile::initTiles method from objdump into standard input

from sys import stdin

lastMov = "";

def decodeAndPrint(movstr):
  endpart = movstr[movstr.find("#") + 1:len(movstr) - 1]
	if endpart.find(";") > -1:
		endpart = endpart[0:endpart.find(";") - 1]
	print(movstr[0:movstr.find(":")].lstrip() + "," + "{0:X}".format(int(endpart)))

def isAConstructor(mystr):
	if mystr.find("bl") < 0 or mystr.find("::") < 0 or mystr.find("Tile") < 0:
		return False;
	funcname = mystr[mystr.find("<") + 1: mystr.find(">")]
	firstPart = funcname[0: funcname.find("::")]
	secondPart = funcname[funcname.find("::") + 2: funcname.find("(")]
	if firstPart == secondPart:
		return True
	return False

for line in stdin:
	if isAConstructor(line):
		decodeAndPrint(lastMov)
	elif line.find("mov") > -1 and line.find("r1, #") > -1:
		lastMov = line

