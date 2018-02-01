from scene import *
from random import choice

def opposite(d):
	return (d[0]*-1, d[1]*-1)
	
def sub_tuples(a, b):
	return (a[0]-b[0], a[1]-b[1])
	
def add_tuples(a, b):
	return (a[0]+b[0], a[1]+b[1])

NORTH = (0, 1)
EAST = (1, 0)
SOUTH = opposite(NORTH)
WEST = opposite(EAST)

dirs = [WEST, SOUTH, EAST, NORTH]

class Cell (object):
	def __init__(self, x, y, size):
		self.x = x
		self.y = y
		self.location = (x, y)
		self.size = size
		self.visited = False
		self.visits = 0
		self.neighbors = []
		self.walls = {}
		self.rect = Rect(x*self.size.w, y*self.size.h, *size)
		self.colr = Color(0,0,0)
		left = self.rect.left()
		right = self.rect.right()
		bottom = self.rect.bottom()
		top = self.rect.top()
		self.lines = {NORTH:(left, top, right, top), SOUTH:(left, bottom, right, bottom),
		                   EAST:(right, bottom, right, top), WEST:(left, bottom, left, top)}
		
	def unvisited_neighbors(self):
		return [c for c in self.neighbors if not c.visited]
		
	def visited_neighbors(self):
		return [c for c in self.neighbors if c.visited]
		
	def draw(self):
		no_stroke()
		fill(*self.colr)
		rect(*self.rect)
		stroke(0.00, 1.00, 0.00)
		stroke_weight(1)
		for wall in self.walls:
			d = sub_tuples(wall, self.location)
			if self.walls[wall]:
				line(*self.lines[d])
				
				
class Maze (Scene):
	def __init__(self, w, h):
		self.grid_size = Size(w, h)
	
	def setup(self):
		cell_size = Size(self.size.w/self.grid_size.w, self.size.h/self.grid_size.h)
		self.cells = [[Cell(x, y, cell_size) for x in xrange(self.grid_size.w)] for y in xrange(self.grid_size.h)]
		
		self.start = self.cells[-1][0]
		self.finish = self.cells[0][-1]
		self.current_cell = self.finish
		self.current_cell.visited = True
		
		#for use with creation algorithm
		self.maze_created = False
		self.hunt_mode = False 
		self.row = []
		################################
		
		self.path = [self.current_cell]
		self.backtrack = [self.start]
		self.user_path = [self.start]
		self.solution = [self.start]
		
		# for use with wall-follower
		self.current_dir = EAST
		self.dir_priority = {NORTH:[WEST, NORTH, EAST, SOUTH], SOUTH:[EAST, SOUTH, WEST, NORTH],
		                EAST:[NORTH, EAST, SOUTH, WEST], WEST:[SOUTH, WEST, NORTH, EAST]}
		############################
		
		self.current_solver = self.wall_follower
		
		self.init_cells()
		
	def init_cells(self):
		w, h = self.grid_size
		for row in self.cells:
			for cell in row:
				for d in dirs:
					x, y = add_tuples(cell.location, d)
					if x>=0 and x<w and y>=0 and y<h:
						cell.neighbors.append(self.cells[y][x])
					cell.walls[(x, y)] = 1
					
	def reset(self):
		self.current_cell = self.finish
		self.path = []
		self.user_path = []
		self.backtrack = []
		for row in self.cells:
			for cell in row:
				cell.visited = False
				cell.visits = 0
				for wall in cell.walls:
					cell.walls[wall] = 1
					
	def unvisited_cells(self):
		return [c for row in self.cells for c in row if not c.visited]
					
	def walk(self, cell):
		cell.visited = True
		cell.walls[self.current_cell.location] = 0
		self.current_cell.walls[cell.location] = 0
		self.current_cell = cell
		self.path.append(cell)
		
	def hunt(self):
		for row in self.cells:
			for cell in row:
				if not cell.visited and len(cell.visited_neighbors()) > 0:
					self.row = row
					self.current_cell = choice(cell.visited_neighbors())
					
	def depth_first_search(self):
		if len(self.unvisited_cells()) > 0 and self.current_cell != self.finish:
			available_neighbors = [c for c in self.current_cell.unvisited_neighbors() if not self.current_cell.walls[c.location]]
			if len(available_neighbors) > 0:
				self.backtrack.append(self.current_cell)
				for d in dirs:
					x, y = add_tuples(d, self.current_cell.location)
					if not self.current_cell.walls[(x, y)]:
						if self.cells[y][x] in available_neighbors:
							next_cell = self.cells[y][x]
				next_cell.visited = True
				self.current_cell.visited = True
				self.current_cell = next_cell
				self.backtrack.append(next_cell)
			else: 
				self.current_cell = self.backtrack.pop(-1)
					
	def wall_follower(self):
		if len(self.unvisited_cells()) > 0 and self.current_cell != self.finish:
			available_neighbors = [c for c in self.current_cell.neighbors if not self.current_cell.walls[c.location]]
			if len(available_neighbors) > 0:
				for d in self.dir_priority[self.current_dir]:
					x, y = add_tuples(d, self.current_cell.location)
					if x in range(self.grid_size.w) and y in range(self.grid_size.h):
						if self.cells[y][x] in available_neighbors:
							self.current_dir = d
							next_cell = self.cells[y][x]
							next_cell.visited = True
							self.current_cell.visited = True
							self.current_cell = next_cell
							self.backtrack.append(self.current_cell)

	def draw(self):
		background(0, 0, 0)
		for row in self.cells:
			for cell in row:
				if cell == self.start:
					cell.colr = Color(0.00, 0.50, 0.00)
				elif cell == self.finish:
					cell.colr = Color(1.00, 0.00, 0.00)
				elif cell == self.current_cell:
					cell.colr = Color(0.00, 0.00, 1.00)
				elif self.hunt_mode and self.row==row:
					cell.colr = Color(0.40, 1.00, 0.40)
				elif cell in self.solution and self.maze_created:
					cell.colr = Color(0.00, 1.00, 0.00)
				elif cell in self.backtrack and self.current_solver != self.wall_follower:
					cell.colr = Color(1.00, 1.00, 0.00)
				elif cell.visited:
					cell.colr = Color(0.00, 0.25, 0.50)
				else: 
					cell.colr = Color(0.00, 0.00, 0.00)
				cell.draw()
		
		if self.maze_created:
			for touch in self.touches.values():
				if touch.location.y > self.size.h*0.5:
					self.current_solver = self.wall_follower
				elif touch.location.y < self.size.h*0.5:
					self.current_solver = self.depth_first_search
				self.current_solver()
					
		if len(self.touches) == 3:
			self.maze_created = False
			self.reset()

		if len(self.unvisited_cells()) > 0 and not self.maze_created:
			if len(self.current_cell.unvisited_neighbors()) > 0:
				self.hunt_mode = False 
				next_cell = choice(self.current_cell.unvisited_neighbors())
				self.walk(next_cell)
			elif len(self.current_cell.unvisited_neighbors()) == 0:
				self.hunt_mode = True
				self.hunt()
				
		elif len(self.unvisited_cells()) == 0:
			if not self.maze_created:
				self.current_cell = self.start
				for row in self.cells:
					for cell in row:
						cell.visited = False
				self.maze_created = True

run(Maze(15, 15))
