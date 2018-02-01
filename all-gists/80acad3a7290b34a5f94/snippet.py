#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import re
import glob
import os
 
# (C) 2015 Ich konzentriere mich völlig auf meine Bachelorarbeit GmbH
# v2: now mildly recursive (depth of 1)
# v3: sortiert die meisten Latexbefehle aus
 
def wordcount(value):
    # Find all non-whitespace patterns.
    words = re.findall("(\S+)", value)
    latex_befehle = re.findall("(\\{\\})", value) + re.findall("(\\\\item)", value)

     # Return length of resulting list.
    return len(words) - len(latex_befehle)
 
def get_latex_files():
	file_list =  glob.glob('*.tex')
	file_list += (glob.glob(os.path.join('*', '*.tex')))
	return file_list
 
 
 
totalwords = 0
total_comment_lines = 0
file_output_format = "{:<25}"
wordcount_output_format = "{:>5}"
 
for filename in get_latex_files():
 
	file = open(filename, 'r')
	print file_output_format.format(filename),
 
	words = 0
 
	for line in file:
		if line[0] != "%":
			words += wordcount(line)
		else:
			total_comment_lines += 1
 
	totalwords += words
	print wordcount_output_format.format(words)
 
print "-" * 31
print file_output_format.format("TOTAL"),
print wordcount_output_format.format(totalwords)
print "(%i Zeilen Kommentar ignoriert)\n" % total_comment_lines
 
