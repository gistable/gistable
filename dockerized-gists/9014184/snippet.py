import pygame, sys, random
from pygame.locals import *

class sim:
	# X origin
	#DELTA = 0.1

	# Windows size#891
	WIN_H = 504.
	WIN_W = 308 + 600
	
	# X origin
	X_ZERO = 100.
	# Y origin
	#Y_ZERO = (WIN_H- 400)/2
	Y_ZERO = (WIN_H - 100.)*0.59
	# X speed
	X_SPEED = 115.#5.69
	# Y acceleration
	#Y_ACC =  1228 #vlc
	#Y_ACC =  1656 #math 
	#Y_ACC =  588 #test 
	Y_ACC =  1414 #other code


	# Max speed
	#MAX_SPEED = 600. #vlc
	#MAX_SPEED = 300. #math
	MAX_SPEED = 400. #feel
	# Min negative speed
	MIN_SPEED = -MAX_SPEED #* 0.75 #-300.
	
	# Jump speed
	J_SPEED = -395. # other code
	#J_SPEED = -420.
	#J_SPEED = -(MAX_SPEED-MIN_SPEED)*0.75 #math

	# Bird size
	BW = 40./504. * WIN_H
	BH = 30./504. * WIN_H

	# Pipe hole size
	PW = 56./504. * WIN_H
	PH = 102./504. * WIN_H

	# Distance between pipes
	P_DISTANCE = 113./504. * WIN_H

	# Ground height
	GH = 100./504. * WIN_H
	
	
	def init(self):
		pygame.init()
		self.win = pygame.display.set_mode((self.WIN_W, int(self.WIN_H)))
		pygame.display.set_caption("Flappy game simulator")
		
		self.clock = pygame.time.Clock()
		
		self.resetState()
		self.newWorld()
		self.max = 600
	def newWorld(self):
		self.pipes = []
		for i in range(0,80):
			r = random.randint(30, self.WIN_H - self.PH - self.GH - 40)
			self.pipes.append(Rect(350 + i*(self.P_DISTANCE + self.PW), 0, self.PW, r))
			self.pipes.append(Rect(350 + i*(self.P_DISTANCE + self.PW), r + self.PH, self.PW, self.WIN_H - self.GH - r - self.PH))	
			#self.pipes.append(Rect(350 + i*(self.P_DISTANCE + self.PW), random.randint(30, self.WIN_H - self.PH - self.GH - 40), self.PW, self.PH))


	def resetState(self):
		self.bird = Rect(self.X_ZERO, self.Y_ZERO, self.BW, self.BH)
		self.bird_speed = self.J_SPEED
	"""
	Draw curve from a to b, with "it" iterations
	"""
	def drawLine(self, a, b, it):
		lines = []
		v = self.bird_speed
		y = self.bird.y
		# a/2t**2 + v0t + y0 = y
		for x in range(a,b,(b-a)/it):
			t = (x-a)/self.X_SPEED
			print (x,self.bird.y + self.Y_ACC*t**2+self.bird_speed*t)
			lines.append((x,self.bird.y + self.Y_ACC*t**2+self.bird_speed*t))
		pygame.draw.lines(self.win, pygame.Color(0,0,255),False, lines)
	def loop(self):
		while True:
			self.updateBird(self.clock.get_time())
			if self.bird.y < self.max:
				self.max = self.bird.y

			self.win.fill(pygame.Color(255,255,255))

			pygame.draw.rect(self.win, pygame.Color(0,0,0), Rect(0, self.WIN_H - self.GH, self.WIN_W, self.GH), 1)

			pygame.draw.rect(self.win, pygame.Color(255,0,0), self.bird, 3)
			self.drawLine(self.bird.x, self.bird.x + 200,100)
			#pygame.draw.rect(self.win, pygame.Color(0,0,0), Rect(0, self.max, self.WIN_W, 1), 1)
			#pygame.draw.rect(self.win, pygame.Color(0,0,0), Rect(0, self.Y_ZERO, self.WIN_W, 1), 1)
			
			
			for p in self.pipes:
				p.x -= self.X_SPEED * self.clock.get_time()/1000
				pygame.draw.rect(self.win, pygame.Color(0,0,0), p, 1)
			
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == MOUSEBUTTONUP:
					if event.button in (1,2,3):
						self.bird_speed += self.J_SPEED
				elif event.type == KEYDOWN:
					if event.key == K_SPACE:
						self.bird_speed += self.J_SPEED
					elif event.key == K_w:
						self.Y_ACC += 10
						print "a=", self.Y_ACC
					elif event.key == K_s:
						self.Y_ACC -= 10
						print "a=", self.Y_ACC
					elif event.key == K_e:
						self.J_SPEED += 10
						print "j=", self.J_SPEED
					elif event.key == K_d:
						self.J_SPEED -= 10
						print "j=", self.J_SPEED
			pygame.display.update()
			self.clock.tick(30)

	def updateBird(self, delta):
		delta = delta/1000.0
		#self.bird.x += self.X_SPEED * delta
		 
		self.bird_speed += self.Y_ACC * delta
		if self.bird_speed < self.MIN_SPEED:
			self.bird_speed = self.MIN_SPEED
		if self.bird_speed > self.MAX_SPEED:
			self.bird_speed = self.MAX_SPEED
			#sleep(1)
		#print self.bird_speed/100.
		self.bird.y += self.bird_speed * delta
		
		
		if self.bird.y + self.BH > self.WIN_H - self.GH:
			self.resetState()
			self.newWorld()
		if self.bird.x + self.BW > self.WIN_W:
			self.bird.x = 0
s = sim()
s.init()
s.loop()