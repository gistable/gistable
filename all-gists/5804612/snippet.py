#!/usr/bin/python
# -*- coding: utf-8 -*-

import curses
from math import floor
from datetime import datetime as date
from subprocess import Popen as popen

# Globals:
screen			= curses.initscr()
last_width		= 0
last_height		= 0
alarm_hour		= 0
alarm_minute	= 0
alarm_state		= False
alarm				= None
glyph				= {
	'0': ["  #####   ", " ##   ##  ", "##     ## ", "##     ## ", "##     ## ", " ##   ##  ", "  #####   "],
	'1': ["    ##    ", "  ####    ", "    ##    ", "    ##    ", "    ##    ", "    ##    ", "  ######  "],
	'2': [" #######  ", "##     ## ", "       ## ", " #######  ", "##        ", "##        ", "######### "],
	'3': [" #######  ", "##     ## ", "       ## ", " #######  ", "       ## ", "##     ## ", " #######  "],
	'4': ["##        ", "##    ##  ", "##    ##  ", "##    ##  ", "######### ", "      ##  ", "      ##  "],
	'5': [" ######## ", " ##       ", " ##       ", " #######  ", "       ## ", " ##    ## ", "  ######  "],
	'6': [" #######  ", "##     ## ", "##        ", "########  ", "##     ## ", "##     ## ", " #######  "],
	'7': [" ######## ", " ##    ## ", "     ##   ", "    ##    ", "   ##     ", "   ##     ", "   ##     "],
	'8': [" #######  ", "##     ## ", "##     ## ", " #######  ", "##     ## ", "##     ## ", " #######  "],
	'9': [" #######  ", "##     ## ", "##     ## ", " ######## ", "       ## ", "##     ## ", " #######  "],
	':': ["   ", "   ", " # ", "   ", " # ", "   ", "   "]
}

def addstr(y, x, string, color):
	try:
				screen.addstr( origin_y + y, origin_x + x, string, color)
				screen.refresh()
	except:	return

def print_time(now):
	time_line	= now.strftime("%I:%M:%S")
	time_array	= ["" for i in range(0,7)]

	# Concat glyphs:
	for char in time_line:
		char_array = glyph[char]
		for row in range(0, len(char_array)):
			time_array[row] += char_array[row]

	# Print glyphs:
	for y in range(0, len(time_array)):
		for x in range(0, len(time_array[y])):
			char	= time_array[y][x]
			color	= 1 if char == " " else 3
			addstr(	y, x, " ",
						curses.color_pair(color))

	# Add meridian:
	addstr(	6, len(time_array[0]), now.strftime("%p"),
				curses.color_pair(2) | curses.A_BOLD)

def print_date(now):
	day_line		= now.strftime("%A").center(11," ")
	date_line	= now.strftime("%B %d, %Y")

	addstr(8, 0, day_line, curses.color_pair(3))
	addstr(8, len(day_line) + 1, date_line, curses.color_pair(2) | curses.A_BOLD)

def print_alarm():
	minute	= alarm_minute
	hour		= alarm_hour - 12 if alarm_hour > 12 else (12 if not alarm_hour else alarm_hour)
	meridian	= "AM" if alarm_hour < 12 else "PM"
	state		= "ACT" if alarm_state else "OFF"
	time		= " %02d:%02d %s " % (hour, minute, meridian)

	addstr(8, 46, state.center(5," "), curses.color_pair(3))
	addstr(8, 52, " < ", curses.color_pair(3))
	addstr(8, 55,  time, curses.color_pair(2) | curses.A_BOLD)
	addstr(8, 65, " > ", curses.color_pair(3))

def step_alarm(direction):
	global alarm_minute, alarm_hour
	alarm_minute = (30 if alarm_minute == 0 else 0)
	if direction and alarm_minute == 0:	alarm_hour = (alarm_hour + 1) % 24
	elif not direction and alarm_minute == 30: alarm_hour = (alarm_hour - 1) % 24

def handle_mouse():
	global alarm_state
	(i, x, y, z, bstate)	= curses.getmouse()

	if y == origin_y + 8 and bstate == curses.BUTTON1_CLICKED:
		if x > origin_x + 51 and x < origin_x + 55:
			step_alarm(False)
		if x > origin_x + 64 and x < origin_x + 68:
			step_alarm(True)
		if x > origin_x + 45 and x < origin_x + 51:
			alarm_state = not alarm_state

# Setup
screen.keypad(1)
curses.curs_set(0)
curses.start_color()
curses.init_pair(1, 0, 0) # BB
curses.init_pair(2, 3, 0) # YB
curses.init_pair(3, 0, 3) # BY
curses.mousemask(curses.ALL_MOUSE_EVENTS)
curses.noecho()
curses.cbreak()

# Main
a = 0
while True:
	width		= screen.getmaxyx()[1]
	height	= screen.getmaxyx()[0]
	origin_x	= floor(width / 2) - 34
	origin_y	= floor(height / 2) - 4
	now		= date.now()

	if width != last_width or height != last_height: screen.clear()
	last_width = width
	last_height = height

	print_time(now)
	print_date(now)
	print_alarm()

	if alarm_state and				\
		int(now.hour)   == alarm_hour and	\
		int(now.minute) == alarm_minute and	\
		int(now.second) == 0:
		pass

	screen.timeout(30)
	char = screen.getch()
	if (char != -1):
		if	char == curses.KEY_MOUSE: handle_mouse()
		elif char == 113: break

# Cleanup:
curses.endwin()
