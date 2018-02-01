#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rgbtorgb.py
#
# Robert Chmielowiec 2010

def rgb_to_rgblong (r, g, b):
	return r * pow (256, 2) + g * 256 + b

def rgblong_to_rgb (rgb):
	return rgb / pow (256, 2), (rgb & 65535 ^ 255) / 256, rgb & 255

def rgb_to_hex(r, g, b):
	return "#%02x%02x%02x" % (r, g, b)

def tests():
	for r in (0, 128, 255):
		for g in (0, 128, 255):
			for b in (0, 128, 255):
				print "rgb_to_rgblong (rgblong_to_rgb (%d, %d, %d)) = %s" % \
					(r, g, b, rgblong_to_rgb (rgb_to_rgblong(r, g, b)))
				print "rgb_to_hex (%d, %d, %d) = %s" % \
					(r, g, b, rgb_to_hex (r, g, b))

if __name__ == '__main__':
	tests ()
