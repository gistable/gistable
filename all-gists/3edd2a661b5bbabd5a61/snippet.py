#!/usr/bin/python
# coding: utf-8

# Copyright (c) 2013 Mountainstorm
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


from types import *
import fcntl
from ctypes import *
from termios import *
import tty
import os
import sys
import io
from select import select
import time


import sys, re
 
CLUT = [  # color look-up table
#    8-bit, RGB hex
 
    # Primary 3-bit (8 colors). Unique representation!
    ('00',  '000000'),
    ('01',  '800000'),
    ('02',  '008000'),
    ('03',  '808000'),
    ('04',  '000080'),
    ('05',  '800080'),
    ('06',  '008080'),
    ('07',  'c0c0c0'),
 
    # Equivalent "bright" versions of original 8 colors.
    ('08',  '808080'),
    ('09',  'ff0000'),
    ('10',  '00ff00'),
    ('11',  'ffff00'),
    ('12',  '0000ff'),
    ('13',  'ff00ff'),
    ('14',  '00ffff'),
    ('15',  'ffffff'),
 
    # Strictly ascending.
    ('16',  '000000'),
    ('17',  '00005f'),
    ('18',  '000087'),
    ('19',  '0000af'),
    ('20',  '0000d7'),
    ('21',  '0000ff'),
    ('22',  '005f00'),
    ('23',  '005f5f'),
    ('24',  '005f87'),
    ('25',  '005faf'),
    ('26',  '005fd7'),
    ('27',  '005fff'),
    ('28',  '008700'),
    ('29',  '00875f'),
    ('30',  '008787'),
    ('31',  '0087af'),
    ('32',  '0087d7'),
    ('33',  '0087ff'),
    ('34',  '00af00'),
    ('35',  '00af5f'),
    ('36',  '00af87'),
    ('37',  '00afaf'),
    ('38',  '00afd7'),
    ('39',  '00afff'),
    ('40',  '00d700'),
    ('41',  '00d75f'),
    ('42',  '00d787'),
    ('43',  '00d7af'),
    ('44',  '00d7d7'),
    ('45',  '00d7ff'),
    ('46',  '00ff00'),
    ('47',  '00ff5f'),
    ('48',  '00ff87'),
    ('49',  '00ffaf'),
    ('50',  '00ffd7'),
    ('51',  '00ffff'),
    ('52',  '5f0000'),
    ('53',  '5f005f'),
    ('54',  '5f0087'),
    ('55',  '5f00af'),
    ('56',  '5f00d7'),
    ('57',  '5f00ff'),
    ('58',  '5f5f00'),
    ('59',  '5f5f5f'),
    ('60',  '5f5f87'),
    ('61',  '5f5faf'),
    ('62',  '5f5fd7'),
    ('63',  '5f5fff'),
    ('64',  '5f8700'),
    ('65',  '5f875f'),
    ('66',  '5f8787'),
    ('67',  '5f87af'),
    ('68',  '5f87d7'),
    ('69',  '5f87ff'),
    ('70',  '5faf00'),
    ('71',  '5faf5f'),
    ('72',  '5faf87'),
    ('73',  '5fafaf'),
    ('74',  '5fafd7'),
    ('75',  '5fafff'),
    ('76',  '5fd700'),
    ('77',  '5fd75f'),
    ('78',  '5fd787'),
    ('79',  '5fd7af'),
    ('80',  '5fd7d7'),
    ('81',  '5fd7ff'),
    ('82',  '5fff00'),
    ('83',  '5fff5f'),
    ('84',  '5fff87'),
    ('85',  '5fffaf'),
    ('86',  '5fffd7'),
    ('87',  '5fffff'),
    ('88',  '870000'),
    ('89',  '87005f'),
    ('90',  '870087'),
    ('91',  '8700af'),
    ('92',  '8700d7'),
    ('93',  '8700ff'),
    ('94',  '875f00'),
    ('95',  '875f5f'),
    ('96',  '875f87'),
    ('97',  '875faf'),
    ('98',  '875fd7'),
    ('99',  '875fff'),
    ('100', '878700'),
    ('101', '87875f'),
    ('102', '878787'),
    ('103', '8787af'),
    ('104', '8787d7'),
    ('105', '8787ff'),
    ('106', '87af00'),
    ('107', '87af5f'),
    ('108', '87af87'),
    ('109', '87afaf'),
    ('110', '87afd7'),
    ('111', '87afff'),
    ('112', '87d700'),
    ('113', '87d75f'),
    ('114', '87d787'),
    ('115', '87d7af'),
    ('116', '87d7d7'),
    ('117', '87d7ff'),
    ('118', '87ff00'),
    ('119', '87ff5f'),
    ('120', '87ff87'),
    ('121', '87ffaf'),
    ('122', '87ffd7'),
    ('123', '87ffff'),
    ('124', 'af0000'),
    ('125', 'af005f'),
    ('126', 'af0087'),
    ('127', 'af00af'),
    ('128', 'af00d7'),
    ('129', 'af00ff'),
    ('130', 'af5f00'),
    ('131', 'af5f5f'),
    ('132', 'af5f87'),
    ('133', 'af5faf'),
    ('134', 'af5fd7'),
    ('135', 'af5fff'),
    ('136', 'af8700'),
    ('137', 'af875f'),
    ('138', 'af8787'),
    ('139', 'af87af'),
    ('140', 'af87d7'),
    ('141', 'af87ff'),
    ('142', 'afaf00'),
    ('143', 'afaf5f'),
    ('144', 'afaf87'),
    ('145', 'afafaf'),
    ('146', 'afafd7'),
    ('147', 'afafff'),
    ('148', 'afd700'),
    ('149', 'afd75f'),
    ('150', 'afd787'),
    ('151', 'afd7af'),
    ('152', 'afd7d7'),
    ('153', 'afd7ff'),
    ('154', 'afff00'),
    ('155', 'afff5f'),
    ('156', 'afff87'),
    ('157', 'afffaf'),
    ('158', 'afffd7'),
    ('159', 'afffff'),
    ('160', 'd70000'),
    ('161', 'd7005f'),
    ('162', 'd70087'),
    ('163', 'd700af'),
    ('164', 'd700d7'),
    ('165', 'd700ff'),
    ('166', 'd75f00'),
    ('167', 'd75f5f'),
    ('168', 'd75f87'),
    ('169', 'd75faf'),
    ('170', 'd75fd7'),
    ('171', 'd75fff'),
    ('172', 'd78700'),
    ('173', 'd7875f'),
    ('174', 'd78787'),
    ('175', 'd787af'),
    ('176', 'd787d7'),
    ('177', 'd787ff'),
    ('178', 'd7af00'),
    ('179', 'd7af5f'),
    ('180', 'd7af87'),
    ('181', 'd7afaf'),
    ('182', 'd7afd7'),
    ('183', 'd7afff'),
    ('184', 'd7d700'),
    ('185', 'd7d75f'),
    ('186', 'd7d787'),
    ('187', 'd7d7af'),
    ('188', 'd7d7d7'),
    ('189', 'd7d7ff'),
    ('190', 'd7ff00'),
    ('191', 'd7ff5f'),
    ('192', 'd7ff87'),
    ('193', 'd7ffaf'),
    ('194', 'd7ffd7'),
    ('195', 'd7ffff'),
    ('196', 'ff0000'),
    ('197', 'ff005f'),
    ('198', 'ff0087'),
    ('199', 'ff00af'),
    ('200', 'ff00d7'),
    ('201', 'ff00ff'),
    ('202', 'ff5f00'),
    ('203', 'ff5f5f'),
    ('204', 'ff5f87'),
    ('205', 'ff5faf'),
    ('206', 'ff5fd7'),
    ('207', 'ff5fff'),
    ('208', 'ff8700'),
    ('209', 'ff875f'),
    ('210', 'ff8787'),
    ('211', 'ff87af'),
    ('212', 'ff87d7'),
    ('213', 'ff87ff'),
    ('214', 'ffaf00'),
    ('215', 'ffaf5f'),
    ('216', 'ffaf87'),
    ('217', 'ffafaf'),
    ('218', 'ffafd7'),
    ('219', 'ffafff'),
    ('220', 'ffd700'),
    ('221', 'ffd75f'),
    ('222', 'ffd787'),
    ('223', 'ffd7af'),
    ('224', 'ffd7d7'),
    ('225', 'ffd7ff'),
    ('226', 'ffff00'),
    ('227', 'ffff5f'),
    ('228', 'ffff87'),
    ('229', 'ffffaf'),
    ('230', 'ffffd7'),
    ('231', 'ffffff'),
 
    # Gray-scale range.
    ('232', '080808'),
    ('233', '121212'),
    ('234', '1c1c1c'),
    ('235', '262626'),
    ('236', '303030'),
    ('237', '3a3a3a'),
    ('238', '444444'),
    ('239', '4e4e4e'),
    ('240', '585858'),
    ('241', '626262'),
    ('242', '6c6c6c'),
    ('243', '767676'),
    ('244', '808080'),
    ('245', '8a8a8a'),
    ('246', '949494'),
    ('247', '9e9e9e'),
    ('248', 'a8a8a8'),
    ('249', 'b2b2b2'),
    ('250', 'bcbcbc'),
    ('251', 'c6c6c6'),
    ('252', 'd0d0d0'),
    ('253', 'dadada'),
    ('254', 'e4e4e4'),
    ('255', 'eeeeee'),
]
 
def _str2hex(hexstr):
    return int(hexstr, 16)
 
def _strip_hash(rgb):
    # Strip leading `#` if exists.
    if rgb.startswith('#'):
        rgb = rgb.lstrip('#')
    return rgb
 
def _create_dicts():
    short2rgb_dict = dict(CLUT)
    rgb2short_dict = {}
    for k, v in short2rgb_dict.items():
        rgb2short_dict[v] = k
    return rgb2short_dict, short2rgb_dict
 
def short2rgb(short):
    return SHORT2RGB_DICT[short]
 
def print_all():
    """ Print all 256 xterm color codes.
    """
    for short, rgb in CLUT:
        sys.stdout.write('\033[48;5;%sm%s:%s' % (short, short, rgb))
        sys.stdout.write("\033[0m  ")
        sys.stdout.write('\033[38;5;%sm%s:%s' % (short, short, rgb))
        sys.stdout.write("\033[0m\n")
    print "Printed all codes."
    print "You can translate a hex or 0-255 code by providing an argument."
 
def rgb2short(rgb):
    """ Find the closest xterm-256 approximation to the given RGB value.
    @param rgb: Hex code representing an RGB value, eg, 'abcdef'
    @returns: String between 0 and 255, compatible with xterm.
    >>> rgb2short('123456')
    ('23', '005f5f')
    >>> rgb2short('ffffff')
    ('231', 'ffffff')
    >>> rgb2short('0DADD6') # vimeo logo
    ('38', '00afd7')
    """
    rgb = _strip_hash(rgb)
    incs = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)
    # Break 6-char RGB code into 3 integer vals.
    parts = [ int(h, 16) for h in re.split(r'(..)(..)(..)', rgb)[1:4] ]
    res = []
    for part in parts:
        i = 0
        while i < len(incs)-1:
            s, b = incs[i], incs[i+1]  # smaller, bigger
            if s <= part <= b:
                s1 = abs(s - part)
                b1 = abs(b - part)
                if s1 < b1: closest = s
                else: closest = b
                res.append(closest)
                break
            i += 1
    #print '***', res
    res = ''.join([ ('%02.x' % i) for i in res ])
    equiv = RGB2SHORT_DICT[ res ]
    #print '***', res, equiv
    return equiv, res
 
RGB2SHORT_DICT, SHORT2RGB_DICT = _create_dicts()


from Path import *




#
# linestyles are 2 tuples of strings, the first element is a string of chars 
# to use for thin lines, and the second for thick lines
#
# the characters in the strings represent:
#   0. horizontal lines
#   1. vertical lines
#   2-17. corners chosen as below
#     2. l0=0 & l1=0 => ╶
#     3. l0=0 & l1=1 => └─
#     4. l0=0 & l1=2 => ─
#     5. l0=0 & l1=3 => ┌
#     6. l0=1 & l1=0 => └
#     7. l0=1 & l1=1 => ╵
#     8. l0=1 & l1=2 => ┘
#     9. l0=1 & l1=3 => │
#    10. l0=2 & l1=0 => ─
#    11. l0=2 & l1=1 => ┘
#    12. l0=2 & l1=2 => ╴
#    12. l0=2 & l1=3 => ┐
#    14. l0=3 & l1=0 => ┌
#    15. l0=3 & l1=1 => │
#    16. l0=3 & l1=2 => ┐
#    17. l0=3 & l1=3 => ╷
#
# For each corner we calculate which quadrant the lines eminating from it are in
#        ╲ ╎ ╱
#         ╲1╱ 
#        ╌2╳0╌
#         ╱3╲
#        ╱ ╎ ╲
# The first line, l0, and the second, l1, these quadrants are then looked up in 
# the table 2-17
#          
LINESTYLE_NONE = None
LINESTYLE_DOUBLEDASH = (u'╌╎╶└─┌└╵┘│─┘╴┐┌│┐╷', u'╍╏╺┗━┏┗╹┛┃━┛╸┓┏┃┓╻')
LINESTYLE_TRIPPLEDASH = (u'┄┆╶└─┌└╵┘│─┘╴┐┌│┐╷', u'┅┇╺┗━┏┗╹┛┃━┛╸┓┏┃┓╻')
LINESTYLE_QUADRUPLEDASH = (u'┈┊╶└─┌└╵┘│─┘╴┐┌│┐╷', u'┉┋╺┗━┏┗╹┛┃━┛╸┓┏┃┓╻')
LINESTYLE_SOLID = (u'─│╶└─┌└╵┘│─┘╴┐┌│┐╷', u'━┃╺┗━┏┗╹┛┃━┛╸┓┏┃┓╻')
LINESTYLE_DOUBLE = (u'═║═╚═╔╚║╝║═╝═╗╔║╗║', u'═║═╚═╔╚║╝║═╝═╗╔║╗║')

LINEWIDTH_THIN = 0
LINEWIDTH_THICK = 1

FILLPATTERN_NONE = u' '
FILLPATTERN_LIGHT = u'░'
FILLPATTERN_MEDIUM = u'▒'
FILLPATTERN_DARK = u'▓'
FILLPATTERN_SOLID = u'█'


class GraphicsContext(Path):
	def __init__(self, term):
		Path.__init__(self)
		self._term = term
		self.linestyle = LINESTYLE_SOLID
		self.linewidth = LINEWIDTH_THIN
		self.fillpattern = FILLPATTERN_NONE
		self.bgcolor = Color.BLACK
		self.fgcolor = Color.WHITE
		self.bold = False
		self.underline = False

	# Saving and Restoring the Current Graphics State
	def save_graphics_state(self):
		pass

	def restore_graphics_state(self):
		pass

	# Painting Paths
	def fill_path(self):
		for path in self._subpaths:
			# we need at least 4 points and be closed to make a fillable path
			if len(path) > 3:
				if path[0].x == path[-1].x and path[0].y == path[-1].y:
					self._fill_polygon(path)

	def stroke_path(self):
		for path in self._subpaths:
			# work in pairs and draw a line between them
			if len(path) > 1:
				for i in range(len(path)-1):
					self._stroke_line(path[i], path[i+1])

				# now fix the corners - each set of three points
				if len(path) > 2:
					# must have 3 points min
					if path[0].x == path[-1].x and path[0].y == path[-1].y:
						# closed path - append second point so we can analyse 
						# all the corners with the same code
						path.append(path[1])

					for i in range(len(path)-2):
						l0 = self._getquadrant(path[i], path[i+1])
						l1 = self._getquadrant(path[i+2], path[i+1])
						ch = self.linestyle[self.linewidth][2+(l0*4)+l1]
						self._stroke(path[i+1].x, path[i+1].y, ch)

	def _getquadrant(self, a, b):
		retval = None
		dx = a.x - b.x
		dy = a.y - b.y
		if abs(dx) > abs(dy):
			# quadrant 0 or 2
			retval = 2
			if dx > 0:
				retval = 0
		else:
			# quadrant 1 or 3
			retval = 1
			if dy > 0:
				retval = 3
		return retval

	# XXX Modifying Clipping Paths

	# Drawing Text
	def show_text_at_point(self, x, y, txt):
		pass

	# XXX Converting Between Device Space and User Space

	def _stroke_line(self, a, b):
		#print "line: ", a, b
		# simple bresenham algorithm - taken from wikipedia
		# XXX make this match the lines drawn by the fill
		dx = abs(b.x-a.x)
		dy = abs(b.y-a.y)

		style = self.linestyle[self.linewidth]
		ch = style[1]
		if dx > dy:
			ch = style[0]
		ch = unichr(ord(ch))
		sx = -1
		if a.x < b.x:
			sx = 1 
		sy = -1
		if a.y < b.y:
			sy = 1

		err = dx-dy
 
 		x = a.x
 		y = a.y
		while True:
			self._stroke(x, y, ch)
			if x == b.x and y == b.y:
				break
			e2 = 2*err
			if e2 > -dy:
				err = err-dy
				x = x+sx

			if x == b.x and y == b.y:
				self._stroke(x, y, ch)
				break
			if e2 < dx:
				err = err+dx
				y = y+sy 

	def _stroke(self, x, y, ch):
		#print x, y
		cell = self._term.cells[y][x]
		cell.glyph = ch
		cell.fgcolor = self.fgcolor
		cell.bgcolor = self.bgcolor
		cell.needs_display = True

	def _fill_polygon(self, path):
		class Edge(object):
			def __init__(self, a, b):
				self.ymin = a
				self.ymax = b
				if b.y < a.y:
					self.ymin = b
					self.ymax = a
				self.x = self.ymin.x
				self.slope = None
				if a.x != b.x:
					self.slope = float(a.y-b.y) / float(a.x-b.x)

			def __repr__(self):
				return "%d.%d" % (self.ymin.y, self.x)

		# insert edges and sort by increasing y and x
		alledges = []
		for i in range(len(path)-1):
			e = Edge(path[i], path[i+1])
			if e.slope != 0:
				for j in range(len(alledges)):
					if e.ymin.y < alledges[j].ymin.y:
						# insert before
						alledges.insert(j, e)
						e = None
						break
					elif e.ymin.y == alledges[j].ymin.y:
						if e.ymin.x < alledges[j].ymin.x:
							# insert before
							alledges.insert(j, e)
							e = None
							break
						else:
							# insert after
							alledges.insert(j+1, e)
							e = None
							break
				if e is not None:
					# insert at end
					alledges.append(e)
		#print alledges
		# setup
		scanline = alledges[0].ymin.y
		activeedges = []
		for i in range(len(alledges)):
			if alledges[i].ymin.y == scanline:
				activeedges.append(alledges[i])
			else:
				break
		
		# fill the polygon
		old = activeedges
		activeedges = []
		for e in old:
			for j in range(len(activeedges)):
				if e.x <= activeedges[j].x:
					# insert before
					activeedges.insert(j, e)
					e = None
					break
			if e is not None:
				activeedges.append(e)
		#print activeedges
		
		while len(activeedges) > 0:
			for i in range(0, len(activeedges), 2):
				#print "fill", activeedges[i].x, activeedges[i+1].x, scanline
				for x in range(int(activeedges[i].x+0.5), int(activeedges[i+1].x+0.5)):
					self._stroke(x, scanline, self.fillpattern)
		
			scanline += 1
			old = activeedges
			activeedges = []
			for e in old:
				if e.ymax.y != scanline:
					activeedges.append(e)
			for e in activeedges:
				if e.slope is not None:
					e.x = e.x + (1 / e.slope)
			for e in alledges:
				if e.ymin.y == scanline:
					activeedges.append(e)
			old = activeedges
			activeedges = []
			for e in old:
				for j in range(len(activeedges)):
					if e.x <= activeedges[j].x:
						# insert before
						activeedges.insert(j, e)
						e = None
						break
				if e is not None:
					activeedges.append(e)

			
if __name__ == u'__main__':
	import math

	out = sys.stdout
	sys.stdout = sys.stderr # ensure output goes somewhere useful
	t = Terminal(out, sys.stdin)
	try:
		gc = GraphicsContext(t)
		
		#d = 0
		#d1 = 0
		#while True:
		#	y = math.cos(math.radians(d)) * 8
		#	x = math.sin(math.radians(d)) * 8
		#	y1 = math.cos(math.radians(d1)) * 4
		#	x1 = math.sin(math.radians(d1)) * 4

		#gc.bgcolor = Color(u'#002b36')
		#gc.add_rect(Rect(0, 0, t.width, t.height))
		#gc.fill_path()

		#gc.fgcolor = Color(u'#d33682')
		#gc.fillpattern = FILLPATTERN_LIGHT
		#gc.linestyle = LINESTYLE_TRIPPLEDASH
		##gc.linewidth = LINEWIDTH_THICK
		#gc.begin_path()
		#gc.move_to_point(Point(5, 5))
		#gc.add_lines([
		#	Point(10, 5),
		#	Point(10, 9),
		#	Point(12, 9),
		#	Point(12, 5),
		#	Point(50, 5),
		#	Point(70, 9),
		#	Point(70, 18),
		#	Point(9, 18),
		#])
		#gc.close_subpath()
		#gc.fill_path()
		#gc.stroke_path()

		#gc.fillpattern = FILLPATTERN_LIGHT
		#gc.linewidth = LINEWIDTH_THICK

		#gc.begin_path()
		#gc.bgcolor = Color(u'#00002e')
		#print d, x, y
		#gc.move_to_point(Point(40+int(x+0.5), 12+int(y+0.5)))
		#gc.add_line_to_point(Point(40, 12))
		#gc.add_line_to_point(Point(40+int(x1+0.5), 12+int(y1+0.5)))
		#gc.move_to_point(Point(0, 0))
		#gc.stroke_path()
		#gc.add_rect(Rect(27, 6, 24, 12))
		#gc.fill_path()
		#
		#gc.begin_path()
		#gc.add_rect(Rect(29, 7, 20, 10))
		#gc.bgcolor = Color(u'#fdf6e3')
		#gc.fill_path()

		#gc.close_subpath()
		#gc.fill_path()

		t.display()
		t.getnextevent()
		#ret = t.getnextevent(0.03)
		#if ret != '' and retval is not None:
		#	break
		#d += 3
		#d1 = (d / 360) * 12

	finally:
		t.close()
	sys.stdout = sys.__stdout__

