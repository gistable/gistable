import Tkinter

class GraphException(Exception):
 def __init__(self, string):
  Exception.__init__(self, string)

class Graph(Tkinter.Canvas):
 def __init__(self, master, **options):
  Tkinter.Canvas.__init__(self, master, **options)
  if 'width' in options and 'height' in options:
   self.width = int(options['width'])
   self.height = int(options['height'])
  else:
   raise GraphException('Must specify a height and width.')
  self.points = []
  self.lines = []
  self.axes = []
  self.border = None
  self.axis_color = '#000'
  self.point_color = '#f00'
  self.border_color = '#000'
  self.line_color = '#00f'
  self.background_color = '#fff'

 def addAxes(self, xmin, xmax, ymin, ymax):
  self.border = self.create_rectangle(xmin, -ymin, xmax, -ymax, tags='all',outline=self.border_color,fill=self.background_color)
  self.axes.append(self.create_line(xmin, 0, xmax, 0, tags='all',fill=self.axis_color))
  self.axes.append(self.create_line(0, -ymin, 0, -ymax, tags='all',fill=self.axis_color))

 def scaleAndCenter(self):
  # Find the scale factor from size of bounding box
  bb = self.bbox('all')
  bbwidth = int(bb[2]) - int(bb[0])
  bbheight = int(bb[3]) - int(bb[1])
  xscale = self.width / bbwidth
  yscale = self.height / bbheight
  # Scale accordingly
  self.scale('all', 0, 0, xscale, yscale)
  # Move to center the image on the canvas
  bb = self.bbox('all')
  bbwidth = int(bb[2]) - int(bb[0])
  bbheight = int(bb[3]) - int(bb[1])
  self.move('all', self.width/2 - bbwidth/2, self.height/2 + bbheight/2)

 def addPoint(self, x, y):
  self.points.append((self.create_line(x-0.5, -y-0.5, x+0.5, -y+0.5, tags='all', fill=self.point_color),
    self.create_line(x+0.5, -y-0.5, x-0.5, -y+0.5, tags='all', fill=self.point_color)))  
 
 def addLine(self, x0, y0, x1, y1):
  self.lines.append(self.create_line(x0, -y0, x1, -y1, tags='all', fill=self.line_color))

 def addMultipointLine(self, points):
  self.create_line(arrow=Tkinter.LAST, arrowshape=(4,4,0), tags='all', fill=self.line_color, *points)

 def setPointColor(self, color):
  self.point_color = color
 
 def setAxisColor(self, color):
  self.axis_color = color
 
 def setBorderColor(self, color):
  self.border_color = color

 def setBackgroundColor(self, color):
  self.background_color = color
 
 def setLineColor(self, color):
  self.line_color = color
 
 def saveToEPSFile(self, filename):
  self.postscript(colormode='color', file=filename)
 
 def clear(self):
  self.delete('all')
