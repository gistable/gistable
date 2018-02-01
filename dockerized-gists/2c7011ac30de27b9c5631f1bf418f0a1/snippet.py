#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Draw psql output as iTerm2 v3 inline graph using matplotlib
# Author: Alexander Korotkov <a.korotkov@postgrespro.ru>

import sys
import re
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import itertools
import numpy as np
import StringIO
import base64
import os

# TODO:
# * handle newlines in data
# * support more output format variations: line styles, spaces etc.

# Couple of escape sequences printing functions
def print_osc():
	if os.environ.get('TERM') == 'screen':
		sys.stdout.write("\033Ptmux;\033\033]")
	else:
		sys.stdout.write("\033]")
def print_st():
	if os.environ.get('TERM') == 'screen':
		sys.stdout.write("\a\033\\")
	else:
		sys.stdout.write("\a")

enc = 'utf-8'
# Pattern for record header in extended format
extRecPattern = re.compile(u'^([─-]\[ RECORD \d+ \](?:-*|─*))(?:\+-*|[┬┼]─*)$')
data = []
colors = itertools.cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])

# Read table from psql
header = sys.stdin.readline().decode(enc)
m = extRecPattern.match(header)
if m:
	# Extended format
	nameLen = len(m.group(1)) - 1
	valueOffset = len(m.group(1)) + 2
	i = 0
	colNames = []
	row = []
	line = sys.stdin.readline().decode(enc)
	while line:
		if not extRecPattern.match(line):
			name = line[:nameLen].rstrip(' ')
			value = line[valueOffset:].rstrip('\n')
			if i == 0:
				colNames.append(name)
			row.append(value)
		else:
			i = i + 1
			data.append(row)
			row = []
		line = sys.stdin.readline().decode(enc)
	data.append(row)
else:
	# Basic format
	colNames = [name.strip(' ') for name in re.split(u'[|│]', header.rstrip('\n'))]
	line = sys.stdin.readline().decode(enc)
	while line:
		parts = re.split(u'[|│]', line.rstrip('\n'))
		if len(parts) == len(colNames):
			row = [value.strip(' ') for value in parts]
			data.append(row)
		line = sys.stdin.readline().decode(enc)

# Setup graph colored white on black
fig = plt.figure(figsize = (8, 6))
ax = fig.add_subplot(1, 1, 1, axisbg = 'k')
ax.title.set_color('white')
ax.yaxis.label.set_color('white')
ax.xaxis.label.set_color('white')
ax.tick_params(axis = 'x', colors = 'white')
ax.tick_params(axis = 'y', colors = 'white')

# Autodetect plot type. Use plot if all the labels are floats.
x = []
try:
	for row in data:
		x.append(float(row[0]))
	chartType = 'plot'
except ValueError:
	chartType = 'bar'

if chartType == 'bar':
	for row in data:
		x.append(row[0])
	index = np.arange(len(data))
	barWidth = 1.0 / float(len(colNames))

# Do draw
for i in range(1, len(colNames)):
	color = colors.next()
	y = []
	for row in data:
		y.append(float(row[i]))
	if chartType == 'plot':
		ax.plot(x, y, label=colNames[i], color = color)
	if chartType == 'bar':
		ax.bar(index + barWidth * (float(i) - 0.5),
				y,
				barWidth,
				label = colNames[i],
				color = color)

if chartType == 'bar':
	plt.xticks(index + 0.5, x)

# Setup legend
legend = ax.legend(loc = 'best', fancybox = True, framealpha = 0.5)
legendFrame = legend.get_frame()
legendFrame.set_color('white')
legendFrame.set_facecolor('black')
legendFrame.set_edgecolor('white')
for text in legend.get_texts():
	text.set_color('white')

plt.xlabel(colNames[0])
ax.grid(True, color = 'w')

for spine in ax.spines:
	ax.spines[spine].set_edgecolor('white')

# Supress warnings in tight_layout 
with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	plt.tight_layout()

# Put inlined image into iTerm2 v3
imgdata = StringIO.StringIO()
plt.savefig(imgdata, format = 'png', transparent = True)
size = imgdata.tell()
imgdata.seek(0)  # rewind the data

print_osc()
sys.stdout.write('1337;File=')
sys.stdout.write('name=' + base64.b64encode('graph.png') + ';')
sys.stdout.write('size=' + str('size') + ';')
sys.stdout.write('inline=1:')
sys.stdout.write(base64.b64encode(imgdata.buf))
print_st()
sys.stdout.write("\n")
