# -*- coding: utf-8 -*-
from scene import *
from phue import Bridge

class PictureAutomation (Scene):
	def setup(self):
		self.bridge = Bridge()
		self.lights = self.bridge.get_light_objects('name')
		self.init_state = self.get_current_state()
		
		self.root_layer = Layer(self.bounds)
		self.image_layers = {}
		self.button_layers = {}
		
		self.image_names = ['000','001','011','111','010','110','100','101']
		
		self.button_visible = 0
		
		self.button_positions = {}
		self.button_positions['Salon'] = Rect(75,200,60,150)
		self.button_positions['Piano'] = Rect(680,260,60,100)
		self.button_positions[u'Entrée'] = Rect(225,290,130,240)
		
		for image in self.image_names:
			self.image_layers[image] = Layer(Rect(0,0,1024,768))
			self.image_layers[image].image = load_image_file('lights/{0}.png'.format(image))
			self.root_layer.add_layer(self.image_layers[image])
			if image == self.init_state:
				self.image_layers[image].alpha = 1
			else:
				self.image_layers[image].alpha = 0
			
		for light in ['Piano', 'Salon', u'Entrée']:
			self.button_layers[light] = Layer(self.button_positions[light])
			self.button_layers[light].background = (Color(0,0,0,self.button_visible))
			self.root_layer.add_layer(self.button_layers[light])		
		
		self.previous_layer = self.image_layers[self.init_state]
	
	def get_current_state(self):
		state = ''
		for light in ['Salon', u'Entrée', 'Piano']:
			if self.lights[light].on:
				state += '1'
			else:
				state += '0'
		return state
				
	def draw(self):
		self.root_layer.update(self.dt)
		self.root_layer.draw()
	
	def touch_began(self, touch):
		print touch.location
		self.previous_layer = self.image_layers[self.get_current_state()]
		
		for button in self.button_layers:
			if touch.layer == self.button_layers[button]:
				if self.lights[button].on:
					self.lights[button].on = False
				else:
					self.lights[button].on = True
				
				self.update_layers()
	
	def update_layers(self):
		self.image_layers[self.get_current_state()].animate('alpha', 1, 1)
		self.previous_layer.animate('alpha', 0, 1)
			
	def pause(self):
		self.previous_layer = self.image_layers[self.get_current_state()]
	
	def resume(self):
		self.update_layers()
	
	def touch_moved(self, touch):
		pass
	
	def touch_ended(self, touch):
		pass

run(PictureAutomation(), orientation=LANDSCAPE)