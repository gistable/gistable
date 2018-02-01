#!/usr/bin/python

import urllib2
import re

response = urllib2.urlopen('http://edu.msu.ru/mfk/pg1.php')
main_list = unicode(response.read(), 'windows-1251')
faculties = re.finditer('<h4>\s*([^<]*)</h4>\s*<p>(.*)</p>', main_list)
response.close()

count_list = []
fac_count = []

for faculty in faculties:
	matches = re.finditer('<a href="pg2\.php\?muk=(\d+)">([^<]*)</a>', faculty.group(2))
	fac_cnt = 0
	
	for href in matches:
		number = href.group(1)
		name = href.group(2)
		new_url = 'http://edu.msu.ru/mfk/pg2.php?muk=' + number
		response = urllib2.urlopen(new_url)
		course = unicode(response.read(), 'windows-1251')
		count = len(list(re.finditer('<li>', course))) - 2
		fac_cnt += count
		count_list.append((count, name, faculty.group(1).strip()))
		response.close()
	
	fac_count.append((fac_cnt, faculty.group(1).strip()))

fac_count.sort()
count_list.sort()

import codecs
file = codecs.open('mfk.txt', 'w', 'utf-8')

for count, name, faculty in count_list:
	file.write("{0:4} | ".format(count) + name + " | " + faculty + '\r\n')
	
file.write('\r\nFaculties rating\r\n\r\n')
for count, faculty in fac_count:
	file.write("{0:4} | ".format(count) + faculty + '\r\n')
	
try:
	from pylab import *
	from matplotlib import pyplot
	import sys
	is_windows = sys.platform.startswith('win')
	if is_windows:
		matplotlib.rc('font', **{'sans-serif' : 'Arial', 
		'family' : 'sans-serif'})
	
	best_count, best_names_nc, best_faculties = zip(*count_list[-10:])
	best_names = [(name if len(name) < 33 else name[:30] + '...') for name in best_names_nc]
	figure = pyplot.figure(figsize=(9, 7))
	plot = figure.add_subplot(111)
	x = arange(len(best_count)) + 0.5
	rects = plot.barh(x, best_count, align='center', height=0.7, color='#aaaaff')
	
	for rect, name in zip(rects, best_names):
		xloc = int(rect.get_width())
		yloc = rect.get_y()+rect.get_height()/2.0
		plot.text(5, yloc, name, horizontalalignment='left', 
			verticalalignment='center', color='black', weight='bold')
	figure.savefig('mfk.png')
	
	best_count, best_faculties_nc = zip(*fac_count)
	best_faculties = [(fac if len(fac) < 33 else fac[:30] + '...') for fac in best_faculties_nc]
	figure2 = pyplot.figure(figsize=(9, 15))
	plot = figure2.add_subplot(111)
	x = arange(len(best_count)) + 0.5
	rects = plot.barh(x, best_count, align='center', height=0.7, color='#aaaaff')
	
	for rect, faculty in zip(rects, best_faculties):
		xloc = int(rect.get_width())
		yloc = rect.get_y()+rect.get_height()/2.0
		plot.text(5, yloc, faculty, horizontalalignment='left', 
			verticalalignment='center', color='black', weight='bold')
	figure2.savefig('best_faculties.png')
	
	pyplot.show()
except e:
	print str(e)
	print 'Library "matplotlib" is not installed, plot cannot be shown.'
