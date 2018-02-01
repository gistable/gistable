#!/usr/bin/python
#
# Sample code for a "Battle for the Petri Dish" cell
#
# Released under the terms of the WTF Public License,
# No warranty express or implied is granted, etc, etc.
#
# I just hacked this together very quickly; improvements are welcome, so please fork the Gist if you'd like to share your improvements.

import sys
import random

MAX_ENERGY = 7
MAX_HP = 5
ACIDITY = 0

firstArgs = sys.stdin.readline().split(" ");
if "BEGIN" in firstArgs[0]:
    print " ".join([str(prop) for prop in [MAX_HP, MAX_ENERGY, ACIDITY]])
    sys.exit();
else:
    arena_width = int(firstArgs[0])
    arena_height = int(firstArgs[1])

# read in dish state
lineno = 0
arena = {}
line = sys.stdin.readline()
while line != "\n":
    charno = 0
    for char in line:
        if char == "\n": break
        arena[str(charno) + "," + str(lineno)] = { "x": int(charno), "y": int(lineno), "symbol": char };
        charno += 1
    line = sys.stdin.readline()
    lineno += 1

# read in cell stats
stats = sys.stdin.readline().split(" ")
cell = { "x": int(stats[0]), "y": int(stats[1]),
         "hp": int(stats[2]), "energy": int(stats[3]) }

# return a dictionary of spaces (with "x,y" keys and space-content values)
# that are adjacent to (x,y) and have content contained in the given list
def adjacent_spaces(point, match_list=None):
    spaces = []
    for dx in [-1,0,1]:
        for dy in [-1,0,1]:
            if(dx == 0 and dy == 0): continue
            coord_str = str(point["x"]+dx) + "," + str(point["y"]+dy)
            if(coord_str in arena and (match_list is None or arena[coord_str]["symbol"] in match_list)):
                spaces.append(arena[coord_str]);
    return spaces

# given two "x,y" strings, return the direction from 1 to 2
def get_direction(point1, point2):
    dx = point2["x"] - point1["x"]
    dy = point2["y"] - point1["y"]
    dx = abs(dx) / (dx or 1)
    dy = abs(dy) / (dy or 1)

    c2d = { "0,0":"-",
            "0,-1":"N", "0,1":"S", "1,0":"E", "-1,0":"W",
            "-1,-1":"NW", "1,-1":"NE", "1,1":"SE", "-1,1":"SW" } 

    return c2d[str(dx) + "," + str(dy)]

nearby = adjacent_spaces(cell)
nearby_enemies = adjacent_spaces(cell, ['x'])
nearby_corpses = adjacent_spaces(cell, ['c'])
nearby_empty = adjacent_spaces(cell, ['.', 'c'])

# if you have the energy and space to divide, do it
if cell["energy"] >= 5 and len(nearby_empty) > 0:
    print "DIVIDE " + get_direction(cell, random.choice(nearby_empty))
    sys.exit();

# if you have two or more nearby enemies, explode if possible
if len(nearby_enemies) > 1 and cell["energy"] > cell["hp"] and cell["hp"] <= 3:
    print "EXPLODE";
    sys.exit()

# if at least one adjacent enemy, attack if possible
if len(nearby_enemies) > 0 and cell["energy"] > 0:
    print "ATTACK " + get_direction(cell, random.choice(nearby_enemies)) + " " + str(min(cell["energy"], 3))
    sys.exit()

# if there's a nearby corpse, eat it if your energy is below max
if len(nearby_corpses) > 0 and cell["energy"] < MAX_ENERGY:
    print "EAT " + get_direction(cell, random.choice(nearby_corpses))
    sys.exit()

print "REST";
