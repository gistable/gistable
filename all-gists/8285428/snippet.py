from scene import *
from random import random
 
class MyScene (Scene):
	def setup(self):
		# This will be called before the first frame is drawn.
		# Set up the root layer and one other layer:
		self.root_layer = Layer(self.bounds)
		center = self.bounds.center()
		self.layer = Layer(Rect(center.x - 64, center.y - 64, 128, 128))
		self.layer.background = Color(0, 0, 0)
		self.layer.image = 'Smiling_2'
		self.root_layer.add_layer(self.layer)
	
	def draw(self):
		# Update and draw our root layer. For a layer-based scene, this
		# is usually all you have to do in the draw method.
		background(0, 0, 0)
		self.root_layer.update(self.dt)
		self.root_layer.draw()
	
	def touch_began(self, touch):
		# Animate the layer to the location of the touch:
		x, y = touch.location.x, touch.location.y
		new_frame = Rect(x - 64, y - 64, 128, 128)
		self.layer.animate('frame', new_frame, 1.0, curve=curve_bounce_out)
		# 
		self.layer.image = 'Smiling_6'
	
	def touch_moved(self, touch):
		pass
	
	def touch_ended(self, touch):
		self.layer.image = 'Smiling_2'
 
run(MyScene())