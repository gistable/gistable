#!/usr/bin/python
# -*- coding: utf-8 -*-
texts =[u"वाराणसी", u"भौगोलिक", u"उपदर्शन"]
signs = [
u'\u0902', u'\u0903', u'\u093e', u'\u093f', u'\u0940', u'\u0941',
u'\u0942', u'\u0943', u'\u0944', u'\u0946', u'\u0947', u'\u0948',
u'\u094a', u'\u094b', u'\u094c', u'\u094d']
limiters = ['.','\"','\'','`','!',';',',','?']

virama = u'\u094d'
text_index = 1
for text in texts:
	lst_chars = []
	for char in text:
		if char in limiters:
			lst_chars.append(char)
		elif char in signs:
			lst_chars[-1] = lst_chars[-1] + char
		else:
			try:
				if lst_chars[-1][-1] == virama:
					lst_chars[-1] = lst_chars[-1] + char
				else:
					lst_chars.append(char)
			except IndexError:
				lst_chars.append(char)

	index = 1
	for syllable in     lst_chars:
		print text_index, index , syllable 
		index+=1
	text_index+=1
