#!/usr/bin/python

# Author: TROiKAS troikas@pathfinder.gr
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import random
import os.path
import os
import datetime
import webbrowser

def rows(x):
	if os.path.exists("./" + file_name):
		os.remove("./" + file_name)
	for y in range(0,x,1):
		num = []

		for i in range(0,5,1):
			x  = random.randrange(1,46,1)
			if x in num:
				x  = random.randrange(1,46,1)
			num.append(x)
		
		jocker = random.randrange(1,21,1)

		name = str(num[0]) + " - " + str(num[1]) + " - " + str(num[2]) + " - " + str(num[3]) + " - " + str(num[4]) + " Joker: " + str(jocker)

		fileObj = open(file_name, "a")
		fileObj.write("Row: " + str(y + 1) + "\n" + name + "\n")
		fileObj.close()
		print "Row: " + str(y + 1) + "\n" + name + "\n"

def check(n):
	if n > 0 and n <= 5:
		rows(int(n))
		s = raw_input("File save it as " + file_name + " Open it? (y/n) ")
		if s == "y":
			webbrowser.open(file_name)
		elif s == "n":
			print "Ok goodbay!!!"
		else:
			print "What?"
	else:
		r = raw_input("Please insert correct number [1-5]: ")
		recheck(r)
		
def recheck(n):
	check(int(n))
	
file_name = raw_input("File name for save? (with out .txt) Or leave blank to have date in the folder name. ")

if file_name == "":
	now = datetime.datetime.now()
	file_name = now.strftime("%d-%m-%Y_%H:%M")

file_name = file_name + ".txt"	
r = raw_input("How many rows [1-5]: ")
		
check(int(r))

