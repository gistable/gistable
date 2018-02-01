# -*- coding: utf-8 -*-
from scene import *
from time import time
from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont


global EventQ

def p_click():
	print('Klick!')

def focus_true():
	return True 

class Event():
	def setup(self, msg_type,msg=None,obj=None):
		self.msg_type = msg_type
		self.msg = msg
		self.obj = obj
	
class Events():
	def __init__(self):
		self.listeners = []
	def add_listener(self, listener):
		self.listeners.append(listener)
	def pass_event(self, event):
		print event.msg_type
		for listener in self.listeners:
			listener(event)
		del event

class TextBuffer():
	def __init__(self, callback=None, got_focus=focus_true):
		self.text = ''
		self.max_len = 50
		self.font_name = 'Helvetica'
		self.font_size = 32.0
		self.text_img = None
		self.text_img_s = None
		self.type_callback = callback
		self.got_focus = got_focus
		self.color = Color(0,0,0)
	def input_char(self, char):
		if char=='backspace':
			self.text=self.text[:-1]
		elif char == 'mode' or char == 'return':
			pass
		elif len(self.text) < self.max_len:
			self.text += char
		if self.text_img:
			del self.text_img
			del self.text_img_s

		self.text_img, self.text_img_s = render_text(self.text, font_name=self.font_name, font_size=self.font_size)
		
		if self.type_callback:
			self.type_callback()
		
	def event_listener(self, e):
		if self.got_focus():
			if e.msg_type == 'KeyPress':
				self.input_char(e.msg)

class EmptyLayer(Layer):
	def __init__(self, frame):
		super(EmptyLayer, self).__init__(frame)
	def touch_began(self, touch):
		if self.superlayer:
			self.superlayer.touch_began(touch)
		
	def touch_ended(self, touch):
		if self.superlayer:
			self.superlayer.touch_ended(touch)
		
	def touch_moved(self, touch):
		if self.superlayer:
			self.superlayer.touch_moved(touch)

class ScrollLayer(Layer):
	def __init__(self, frame, sublayer, orientation_y = True):
		super(ScrollLayer, self).__init__(frame)
		self.orientation_y = orientation_y
		self.sub_layer = None
		self.stroke=Color(0,0,0)
		self.stroke_weight = 1
		self.set_layer(sublayer)
		self.cover1 = None 
		self.cover2 = None 
	def scrollTo(self, xy):
		if xy < 0:
			self.scrollTo(0)
		elif xy > self.scroll_range:
			self.scrollTo(self.scroll_range)
		else:
			self.scroll_pos = xy
			if self.orientation_y:
				self.sub_layer.frame.y = self.frame.h -self.sub_layer.frame.h + xy
			else:
				self.sub_layer.frame.x = self.frame.w -self.sub_layer.frame.w + xy
	def scrollBy(self, dy):
		self.scrollTo(self.scroll_pos + dy)
	def touch_moved(self, touch):
		if self.orientation_y:
			self.scrollBy((touch.location.y - touch.prev_location.y))
		else:
			self.scrollBy((touch.location.x - touch.prev_location.x))
		self.superlayer.touch_moved(touch)
	def set_layer(self, sublayer):
		if self.sub_layer:
			self.sub_layer.remove_layer()
		self.sub_layer = sublayer
		self.add_layer(self.sub_layer)
		# zero when upper left corners match
		if self.orientation_y:
			scroll_range = self.sub_layer.frame.h - self.frame.h
		else:
			scroll_range = self.sub_layer.frame.w - self.frame.w
		if scroll_range < 0: scroll_range = 0
		self.scroll_range = scroll_range
		self.scroll_pos = scroll_range
		
		if self.sub_layer.frame.h > self.frame.h or self.sub_layer.frame.w > self.frame.w:
			if self.orientation_y:
				self.cover1 = Layer(Rect(0, self.frame.h+1, self.frame.w, self.sub_layer.frame.h))
				self.cover2 = Layer(Rect(0, 0, self.frame.w, 0-self.sub_layer.frame.h))
			else:
				self.cover1 = Layer(Rect(0-1, 0, 0-self.sub_layer.frame.w, self.sub_layer.frame.h))
				self.cover2 = Layer(Rect(self.frame.w+1, 0, self.sub_layer.frame.w, self.sub_layer.frame.h))
			self.cover1.tint = Color(1,1,1)
			self.cover1.background = Color(0,0,0)
			self.add_layer(self.cover1)
			self.cover2.tint = Color(1,1,1)
			self.cover2.background = Color(0,0,0)
			self.add_layer(self.cover2)
			self.scrollTo(0)
	def touch_began(self, touch):
		self.superlayer.touch_began(touch)
	def touch_ended(self, touch):
		self.superlayer.touch_ended(touch)
	def event_listener(self, e):
		if e.msg_type == 'touch_moved':
			if self.frame.intersects(Rect(e.obj.location.x, e.obj.location.y, 1,1)):
				self.touch_moved(e.obj)
	
class Textbox(ScrollLayer):
	def __init__(self, frame):
		super(Textbox, self).__init__(frame, Layer(Rect(0,0,1,1)), orientation_y = False)
		img = Image.new('RGBA',(frame.w,frame.h), 'grey')
		draw = ImageDraw.Draw(img)
		draw.rectangle((1,1, frame.w-2, frame.h-2), outline=256)
		del draw
		self.il = load_pil_image(img)
		self.image = load_pil_image(img)
		self.txtbf = TextBuffer(self.load_new_text, self.got_focus)
		EventQ.add_listener(self.txtbf.event_listener)
		self.textlayer = Layer(Rect(0,0,10,10)) 
		self.focus = False
		self.last_touch = 0
		self.last_click = 0
	def got_focus(self):
		return self.focus
	def load_new_text(self):
		if self.textlayer:
			self.remove_layer(self.textlayer)
		self.textlayer = EmptyLayer(Rect(10,5,self.txtbf.text_img_s.w, self.txtbf.text_img_s.h))
		self.textlayer.tint = self.txtbf.color
		self.textlayer.image=self.txtbf.text_img
		self.set_layer(self.textlayer)
	def touch_ended(self, touch):
		if time() - self.last_touch < 0.2:
			# click
			if self.frame.intersects(Rect(touch.location.x, touch.location.y, 1,1)):
				if self.focus == False:
					self.focus = True
					e = Event()
					e.setup('input_focus','',self)
					EventQ.pass_event(e)
		self.superlayer.touch_ended(touch)
	def touch_began(self, touch):
		self.last_touch = time()
		self.superlayer.touch_began(touch)
	def touch_moved(self, touch):
		self.last_touch = 0 # cancel click
		super(Textbox,self).touch_moved(touch)
		self.superlayer.touch_moved(touch)
			

class RootLayer(Layer):
	def __init__(self, the_scene, frame):
		super(RootLayer, self).__init__(frame)
		self.the_scene = the_scene
	def touch_began(self, touch):
		self.the_scene.touch_began(touch)
		
	def touch_ended(self, touch):
		self.the_scene.touch_ended(touch)
		
	def touch_moved(self, touch):
		self.the_scene.touch_moved(touch)

class KbdLayer(Layer):
	def __init__(self, frame):
		super(KbdLayer, self).__init__(frame)
		self.row_keys = []
		self.n_row_keys = []
		self.setup_keys()
		self.shift = False
		self.direct_input = None
		self.keyboard, self.kb_size = self.load_keyboard()
		self.num_keyboard, self.n_kb_size = self.load_num_keyboard()
		self.frame = Rect(self.frame.x, self.frame.y, 320, 240)
		self.background = Color(0, 0, 0)
		self.image = self.keyboard
		self.mode = 0 # 0: letters. 1: numbers
	def setup_keys(self):
		row1_keys = ['q','w','e','r','t','y','u','i','o','p']
		self.row_keys.append(row1_keys)
		row2_keys = ['a','s','d','f','g','h','j','k','l']
		self.row_keys.append(row2_keys)
		row3_keys = ['shift','z','x','c','v','b','n','m','backspace']
		self.row_keys.append(row3_keys)
		row4_keys = ['mode','space','return']
		self.row_keys.append(row4_keys)
		n_row1_keys = ['1','2','3','4','5','6','7','8','9','0']
		self.n_row_keys.append(n_row1_keys)
		n_row2_keys = ['-','/',':',';','(',')','$','&','@','"']
		self.n_row_keys.append(n_row2_keys)
		n_row3_keys = ['#+=','.',',','?','!',"'",'backspace']
		self.n_row_keys.append(n_row3_keys)
		n_row4_keys = ['mode','space','return']
		self.n_row_keys.append(n_row4_keys)
	def load_keyboard(self):
		kb_filename = "kbd.png"
		kb_image = load_image_file(kb_filename)
		return [kb_image, Image.open(kb_filename).size]
	def load_num_keyboard(self):
		kb_filename = "nkbd.png"
		kb_image = load_image_file(kb_filename)
		return [kb_image, Image.open(kb_filename).size]
	def touch_began(self, touch):
		self.last_touch = time()
		self.superlayer.touch_began(touch)
		
	def touch_ended(self, touch):
		if time() - self.last_touch < 0.2:
			char = ''
			if self.mode == 0: # The alfabetical keyboard
				if touch.location.y > 156:
					i = int(touch.location.x / 32)
					char = self.row_keys[0][i]
					if self.shift:
						char= char.upper()
						self.shift = False 
				elif touch.location.y > 104 and touch.location.y < 146:
					i = int((touch.location.x - 16)/ 32)
					if i > -1 and i < 9:
						char = self.row_keys[1][i]
						if self.shift:
							char= char.upper()
							self.shift = False 
				elif touch.location.y > 52 and touch.location.y < 93:
					if touch.location.x < 41:
						if self.shift:
							self.shift = False
						else:
							self.shift = True
						pass
					elif touch.location.x > 280:
						char = 'backspace'
					else:
						i = int((touch.location.x - 48)/ 32)
						if i > -1 and i < 8:
							char = self.row_keys[2][i]
							if self.shift:
								char= char.upper()
								self.shift = False 
				elif touch.location.y < 41:
					if touch.location.x < 79:
						self.mode = 1
						self.image = self.num_keyboard
					elif touch.location.x < 240:
						char = ' '
					else: 
						char = 'return'
			elif self.mode == 1: # Numerical keyboard
				if touch.location.y > 156:
					i = int(touch.location.x / 32)
					char = self.n_row_keys[0][i]
				elif touch.location.y > 104 and touch.location.y < 146:
					i = int(touch.location.x / 32)
					char = self.n_row_keys[1][i]
				elif touch.location.y > 52 and touch.location.y < 93:
					if touch.location.x < 41:
						pass # The advanced keyboard, to be implemented
					elif touch.location.x > 280:
						char = 'backspace'
					else:
						i = int((touch.location.x - 56)/ 40)
						if i > -1 and i < 6:
							char = self.n_row_keys[2][i]
				elif touch.location.y < 41:
					if touch.location.x < 79:
						self.mode = 0
						self.image = self.keyboard
					elif touch.location.x < 240:
						char = ' '
					else: 
						char = 'return'

			if len(char) > 0:
				if self.direct_input:
					self.direct_input(char)
				else:
					e = Event()
					e.setup('KeyPress', char)
					EventQ.pass_event(e)
		self.superlayer.touch_ended(touch)
	def touch_moved(self, touch):
		self.superlayer.touch_moved(touch)


class MyScene (Scene):
	def setup(self):
		self.touch_start_t = -1
		self.touch_start = Touch(0,0,0,0,0)
		self.hold_timeout = 0
		self.root_layer = RootLayer(self, self.bounds)
		center = self.bounds.center()
		self.kbd_visible = False  
		self.klayer = KbdLayer(Rect(0, 0, 1,1))
		self.input_focus = None 
		#self.root_layer.add_layer(self.klayer)
		self.tbox = Textbox(Rect(self.bounds.w/2-125,self.bounds.h*.75-25,250,50))
		self.root_layer.add_layer(self.tbox)
		EventQ.add_listener(self.tbox.event_listener)
		EventQ.add_listener(self.event_listener)
	def event_listener(self, e):
		if e.msg_type == 'show_keyboard':
			if self.kbd_visible == False:
				self.kbd_visible = True
				self.root_layer.add_layer(self.klayer)
		elif e.msg_type == 'hide_keyboard':
			if self.kbd_visible == True:
				self.root_layer.remove_layer(self.klayer)
				self.kbd_visible = False
		elif e.msg_type == 'input_focus':
			self.input_focus = e.obj
			if self.kbd_visible == False:
				self.kbd_visible = True
				self.root_layer.add_layer(self.klayer)
			self.klayer.direct_input = e.obj.txtbf.input_char
	def draw(self):
		# Update and draw our root layer. For a layer-based scene, this
		# is usually all you have to do in the draw method.
		background(0, 0, 0)
		stroke(1,0,0)
		stroke_weight(1)
		self.root_layer.update(self.dt)
		self.root_layer.draw()
	def touch_began(self, touch):
		self.touch_start = touch
		self.touch_start_t = self.t
	
	def touch_moved(self, touch):
		pass
		
	def touch_ended(self, touch):
		if self.input_focus:

			if touch.location in self.input_focus.frame or touch.location in self.klayer.frame:
				pass
			else:
				self.input_focus.focus = False 
				self.input_focus = None 
				self.klayer.direct_input = None
				if self.kbd_visible == True:
					self.root_layer.remove_layer(self.klayer)
					self.kbd_visible = False

EventQ = Events()
run(MyScene())
