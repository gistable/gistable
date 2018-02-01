"""
Generator for packed circle cartograms
"""
import proj, gisutils

class Cartogram:

	def loadCSV(self, url, key='id', value='val', lon='lon', lat='lat'):
		import csv
		doc = csv.reader(open(url))
		head = None
		circles = []
		for row in doc:
			if not head:
				head = row
			else:
				circles.append(Circle(row[head.index(lon)], row[head.index(lat)], row[head.index(key)], row[head.index(value)]))
			self.circles = circles
		self.computeRadii()
		
	def computeRadii(self):
		import sys, math
		minv = 0
		maxv = sys.maxint * -1
		for c in self.circles:
			minv = min(minv, c.value)
			maxv = max(maxv, c.value)
			
		for c in self.circles:
			c.r = math.pow((c.value - minv)/(maxv-minv), 0.5)*20
	
	def project(self, globe):
		# create view..
		self.globe = globe
		bbox = gisutils.Bounds2D()
		for circle in self.circles:
			x,y = globe.project(circle.lon, circle.lat)
			bbox.update(gisutils.Point(x,y))
		self.bbox = bbox
		w = 700
		self.view = gisutils.View(bbox, w, w*(bbox.height/bbox.width), 80)
		# .. and place circles. you can use any other geo-libs as well, e.g. pyproj
		for circle in self.circles:
			x,y = self.view.project(globe.project(circle.lon, circle.lat))
			circle.x = x 
			circle.y = y
	
	
	def layout(self, steps=100):
		for i in range(steps):
			if i % 10 == 0:
				self.toSVG()
			self.layout_step()			
	
	
	def layout_step(self):
		import math
		pad = 0
			
		for A in self.circles:
			for B in self.circles:
				if A != B:
					radsq = (A.r+B.r)*(A.r+B.r)
					d = A.sqdist(B)
					if radsq + pad > d:
						# move circles away from each other
						v = Vector(B.x-A.x, B.y-A.y)
						v.normalize()
						m = (math.sqrt(radsq) - math.sqrt(d)) * 0.25
						v.resize(m)
						A._move(v.x*-1, v.y*-1)
						B._move(v.x, v.y)
		
		for C in self.circles:
			C.move()
		
						
		
	def toSVG(self):
		from svgfig import SVG, canvas
		w = self.view.width
		h = self.view.height
		svg = canvas(width='%dpx' % w, height='%dpx' % h, viewBox='0 0 %d %d' % (w, h), enable_background='new 0 0 %d %d' % (w, h), style='stroke-width:0.7pt; stroke-linejoin: round; stroke:#444; fill:#eee;')
		
		g = SVG('g', id="gemeinden")
		
		
		for circle in self.circles:
			c = SVG('circle',cx=circle.x, cy=circle.y, r=circle.r)
			c['data-key'] = circle.id
			c['data-population'] = circle.value
			g.append(c)
			
		meta = SVG('metadata')
		views = SVG('views')
		view = SVG('view', padding="80", w=w, h=h)
		proj = self.globe.toXML()
		bbox = self.bbox
		bbox = SVG('bbox', x=round(bbox.left,2), y=round(bbox.top,2), w=round(bbox.width,2), h=round(bbox.height,2))
		
		views.append(view)
		view.append(proj)
		view.append(bbox)
		
		meta.append(views)
		svg.append(meta)
		svg.append(g)
			
		svg.save('cartogram.svg')
		
		
				
class Circle:

	def __init__(self, lon, lat, id, value):
		self.lon = float(lon)
		self.lat = float(lat)
		self.id = id
		self.value = float(value)
		
		self.dx = 0
		self.dy = 0
		
	def _move(self, x,y):
		self.dx += x
		self.dy += y
		
	def move(self):
		self.x += self.dx
		self.y += self.dy
		self.dx = 0
		self.dy = 0
		
	def __repr__(self):
		return '<Circle lon=%f, lat=%f, id=%s, val=%f >'% (self.lon, self.lat, self.id, self.value)
		
	def sqdist(self, circ):
		dx = self.x - circ.x
		dy = self.y - circ.y
		return dx*dx + dy*dy
		

"""
been too lazy to code this myself, instead I took code from here
http://www.kokkugia.com/wiki/index.php5?title=Python_vector_class
"""

class Vector:
    # Class properties
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    # represent as a string
    def __repr__(self):
        return 'Vector(%s, %s)' % (self.x, self.y)

    ''' 
       Class Methods / Behaviours
    '''

    def zero(self):
        self.x = 0.0
        self.y = 0.0
        return self

    def clone(self):
        return kVec(self.x, self.y)

    def normalize(self):
    	from math import sqrt
    	if self.x == 0 and self.y == 0:
    		return self
        norm = float (1.0 / sqrt(self.x*self.x + self.y*self.y))
        self.x *= norm
        self.y *= norm
        # self.z *= norm
        return self

    def invert(self):
        self.x = -(self.x)
        self.y = -(self.y)
        return self

    def resize(self, sizeFactor):
        self.normalize
        self.scale(sizeFactor)
        return self

    def minus(self, t):
        self.x -= t.x
        self.y -= t.y
        # self.z -= t.z
        return self
    
    def plus(self, t):
        self.x += t.x
        self.y += t.y
        # self.z += t.z
        return self
    
    def roundToInt(self):
        self.x = int(x)
        self.y = int(y)
        return self
    
    # Returns the squared length of this vector.
    def lengthSquared(self):
        return float((self.x*self.x) + (self.y*self.y))
    
    # Returns the length of this vector.
    def length(self):
    	from math import sqrt
        return float(sqrt(self.x*self.x + self.y*self.y))

    # Computes the dot product of this vector and vector v2
    def dot(self, v2):
        return (self.x * v2.x + self.y * v2.y)

    # Linearly interpolates between vectors v1 and v2 and returns the result point = (1-alpha)*v1 + alpha*v2.
    def interpolate(self, v2):
        self.x = float((1 - alpha) * self.x + alpha * v2.x)
        self.y = float((1 - alpha) * self.y + alpha * v2.y)
        return kVec(self.x, self.y)

    # Returns the angle in radians between this vector and the vector parameter; 
    # the return value is constrained to the range [0,PI].
    def angle(self, v2):
    	from math import acos
        vDot = self.dot(v2) / (self.length() * v2.length())
        if vDot < -1.0 : vDot = -1.0
        if vDot > 1.0 : vDot = 1.0
        return float(acos(vDot))
    
    # Limits this vector to a given size.
    # NODEBOX USERS: name should change as 'size' and 'scale' are reserved words in Nodebox!
    def limit(self, size):
        if (self.length() > size):
            self.normalize()
            self.scale(size)

    # Point Methods
    # Returns the square of the distance between this tuple and tuple t1.
    def distanceSquared(self, t1):
        dx = self.x - t1.x
        dy = self.y - t1.y
        return (dx * dx + dy * dy)
    
    # NODEBOX USERS: name should change as 'scale' is reserved word in Nodebox!
    def scale(self, s):
        self.x *= s
        self.y *= s
        return self

    # NODEBOX USERS: name should change as 'translate' is reserved word in Nodebox!
    def translate(self, vec):
        self.plus(vec)
        
    # NODEBOX USERS: name should change as 'translate' is reserved word in Nodebox!
    def translate(self, vec, dist):
        v = kVec.resize(vec, dist)
        translation(v)
        
    def distance(self, pt):
    	from math import sqrt
        dx = self.x - pt.x
        dy = self.y - pt.y
        return float(sqrt(dx * dx + dy * dy))
