
# ported from http://www.gizma.com/easing/
# by http://th0ma5w.github.io
#
# untested :P


import math

linearTween = lambda t, b, c, d : c*t/d + b

def easeInQuad(t, b, c, d):
	t /= d
	return c*t*t + b


def easeOutQuad(t, b, c, d):
	t /= d
	return -c * t*(t-2) + b

def easeInOutQuad(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t + b
	t-=1
	return -c/2 * (t*(t-2) - 1) + b


def easeInOutCubic(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t*t + b
	t -= 2
	return c/2*(t*t*t + 2) + b

def easeInQuart(t, b, c, d):
	t /= d
	return c*t*t*t*t + b

def easeOutQuart(t, b, c, d):
	t /= d
	t -= 1
	return -c * (t*t*t*t - 1) + b

def easeInOutQuart(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t*t*t + b
	t -= 2
	return -c/2 * (t*t*t*t - 2) + b

def easeInQuint(t, b, c, d):
	t /= d
	return c*t*t*t*t*t + b

def easeOutQuint(t, b, c, d):
	t /= d
	t -= 1
	return c*(t*t*t*t*t + 1) + b

def easeInOutQuint(t, b, c, d):
	t /= d/2
	if t < 1:
		return c/2*t*t*t*t*t + b
	t -= 2
	return c/2*(t*t*t*t*t + 2) + b

def easeInSine(t, b, c, d):
	return -c * math.cos(t/d * (math.pi/2)) + c + b

def easeOutSine(t, b, c, d):
	return c * math.sin(t/d * (math.pi/2)) + b


def easeInOutSine(t, b, c, d):
	return -c/2 * (math.cos(math.pi*t/d) - 1) + b

def easeInExpo(t, b, c, d):
	return c * math.pow( 2, 10 * (t/d - 1) ) + b

def easeOutExpo(t, b, c, d):
	return c * ( -math.pow( 2, -10 * t/d ) + 1 ) + b


def easeInOutExpo(t, b, c, d):
	t /= d/2
	if t < 1: 
		return c/2 * math.pow( 2, 10 * (t - 1) ) + b
	t -= 1
	return c/2 * ( -math.pow( 2, -10 * t) + 2 ) + b

def easeInCirc(t, b, c, d):
	t /= d
	return -c * (math.sqrt(1 - t*t) - 1) + b

def easeOutCirc(t, b, c, d):
	t /= d;
	t -= 1
	return c * math.sqrt(1 - t*t) + b

def easeInOutCirc(t, b, c, d):
	t /= d/2
	if t < 1:
		return -c/2 * (math.sqrt(1 - t*t) - 1) + b
	t -= 2
	return c/2 * (math.sqrt(1 - t*t) + 1) + b
