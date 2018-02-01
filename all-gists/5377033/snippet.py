import time
import sound
from scene import *
		

class TeaTimer(Scene):
	def setup(self):
		self.initial_time = int(60 * 1.5)
		self.remaining_time = self.initial_time
		self.center_x = self.size.w * 0.5
		self.center_y = self.size.h * 0.5
		self._state = 'start'
	
	def decrement_remaining_time(self):
		self.remaining_time -= 1
	
	def start(self):
		self._state = 'running'
		
		# Set all the delays. This kinda sucks & is ripe for fixing somehow.
		for i in range(self.initial_time):
			self.delay(i, self.decrement_remaining_time)
	
	def time_remaining(self):
		return {
			'minutes': int(self.remaining_time / 60),
			'seconds': int(self.remaining_time % 60),
		}
	
	def draw(self):
		background(0, 0, 0)
		text("Tea will be done in:", font_size=32, x=self.center_x, y=self.center_y+80)
		time_left = self.time_remaining()
		
		# Update the text layer.
		text(
			"{0} min, {1} sec".format(time_left['minutes'], time_left['seconds']),
		    font_size=80.0,
			x=self.center_x,
			y=self.center_y
		)
		
		if self.remaining_time <= 0:
			# Sound + alert that it's finished.
			if not self._state == 'complete':
				self.stop()
	
	def done_alert(self):
		sound.play_effect('Piano_C3')
		sound.play_effect('Piano_E3')
		sound.play_effect('Piano_G3')
			
	def stop(self):
		self._state = 'complete'
		
		for i in range(3):
			self.delay(i, self.done_alert)
		
	def touch_began(self, touch):
		pass
	
	def touch_moved(self, touch):
		pass

	def touch_ended(self, touch):
		if self._state == 'start':
			self.start()
		elif self._state == 'running':
			# Stop & clear.
			pass
		elif self._state == 'complete':
			self._state = 'start'
			self.remaining_time = self.initial_time


run(TeaTimer())
