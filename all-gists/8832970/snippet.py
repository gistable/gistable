# -*- coding: utf-8 -*-
# Conway's game of life.
# Touch cells to give them life.
# Tap screen with two fingers to pause/un-pause.
# Tap screen with three fingers to give life to random cells.

from scene import *
from PIL import Image, ImageDraw
import random

class Cell (object):
	def __init__(self, x, y, frame):
		self.frame = frame
		self.pos = (x, y)
		self.alive = 0
		self.neighbors = []
		self.background = Color(0,0,0)
	
	def update(self, b=None):
		if b is not None:
			self.alive = b
		self.background = Color(1,1,1) if self.alive else Color(0,0,0)
		
	def living_neighbors(self):
		return [c for c in self.neighbors if c.alive]
		
	def draw(self):
		fill(*self.background)
		rect(*self.frame)


class Grid (object):
	def __init__(self, w, h):
		self.size = Size(w, h)
		w, h = (screen.w/w, screen.h/h)
		self.cells = {(x, y):Cell(x, y, Rect(x*w, y*h, w, h)) for x in xrange(self.size.w) for y in xrange(self.size.h)}
		for c in self.cells.values():
			self.adjacent_cells(c)

		grid_img = Image.new('RGBA', [int(i) for i in screen.as_tuple()])
		grid_draw = ImageDraw.Draw(grid_img)
		for x in xrange(self.size.w): grid_draw.line((x*w, 0, x*w, screen.h))
		for y in xrange(self.size.h): grid_draw.line((0, y*h, screen.w, y*h))
		self.grid_img = load_pil_image(grid_img)
		del grid_img, grid_draw
		
	def __iter__(self):
		return iter(sorted(self.cells.keys()))
		
	def __getitem__(self, key):
		return self.cells[key]
		
	def itervalues(self):
		return iter(self.cells.values())
		
	def create_life(self, pos_list=None):
		if pos_list is None:
			w, h = self.size
			for i in xrange(int((w*h)**0.5)*2):
				self.cells[(random.randint(0,w-1), random.randint(0,h-1))].update(1)
		else: 
			for p in pos_list:
				self.cells[p].update(1)
				
	def living_cells(self):
		return [c for c in self.cells.values() if c.alive]
		
	def dead_cells(self):
		return [c for c in self.cells.values() if not c.alive]
			
	def adjacent_cells(self, cell):
		w, h = self.size
		cx, cy = cell.pos
		for y in (-1,0,1):
			for x in (-1,0,1):
				nx = cx+x
				ny = cy+y
				if x == y == 0:
					continue
				if nx>=0 and nx<w and ny>=0 and ny<h:
					cell.neighbors.append(self[(nx, ny)])
					
	def update(self):
		kill = []
		life = []
		
		for cell in self.dead_cells():
			if len(cell.living_neighbors()) == 3:
				life.append(cell)
		for cell in self.living_cells():
			if len(cell.living_neighbors()) < 2:
				kill.append(cell)
			elif len(cell.living_neighbors()) > 3:
				kill.append(cell)
			else:
				life.append(cell)
				
		for k in kill:
			self.cells[k.pos].update(0)
		for l in life:
			self.cells[l.pos].update(1)
			
	def draw(self):
		stroke(1,1,1)
		stroke_weight(1)
		image(self.grid_img, 0, 0)


class MyScene (Scene):
	def setup(self):
		global screen
		screen = self.size
		self.paused = True
		self.grid = Grid(50, 35)
		for c in self.grid.itervalues():
			c.update()
		
	def draw(self):
		background(0,0,0)
		for c in self.grid.living_cells():
			c.draw()
		self.grid.draw()
		if not self.paused:
			if len(self.grid.living_cells()) == 0:
				self.paused = True
			if self.grid.living_cells() > 0:
				self.grid.update()
				
		for touch in self.touches.values():
			if len(self.touches) == 1:
				for cell in self.grid.itervalues():
					if touch.location in cell.frame:
						cell.update(1)
				
	def touch_began(self, touch):
		if len(self.touches) > 1:
			self.paused = True if not self.paused else False
			if len(self.touches) == 3:
				self.grid.create_life()
			
		
run(MyScene())
