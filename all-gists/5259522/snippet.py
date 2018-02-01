#!/usr/bin/env python

import sys

files = []
if len(sys.argv) > 2:
	for file in sys.argv[1:]:
		files.append(str(file))
else:
	print "Usage: Wordcount.py file1 file2 file3 ..."
	
words_to_ignore = ["that","what","with","this","would","from","your","which","while","these"]
things_to_strip = [".",",","?",")","(","\"",":",";","'s"]
words_min_size = 4
print_in_html = True


text = ""
for file in files:
	f = open(file,"rU")
	for line in f:
		text += line

words = text.lower().split()
wordcount = {}
for word in words:
	for thing in things_to_strip:
		if thing in word:
			word = word.replace(thing,"")
	if word not in words_to_ignore and len(word) >= words_min_size:
		if word in wordcount:
			wordcount[word] += 1
		else:
			wordcount[word] = 1
		
sortedbyfrequency =  sorted(wordcount,key=wordcount.get,reverse=True)

def print_txt(sortedbyfrequency):
	for word in sortedbyfrequency:
		print word, wordcount[word]
def print_html(sortedbyfrequency):
	print "<html><head><title>Wordcount.py Output</title></head><body><table>"
	for word in sortedbyfrequency:
		print "<tr><td>%s</td><td>%s</td></tr>" % (word,wordcount[word])
	print "</table></body></html>"

if print_in_html == True:
	print_html(sortedbyfrequency)
else:
	print_txt(sortedbyfrequency)