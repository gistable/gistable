from scene import *
from random import choice, randrange
import sound

TILE_SIZE=64 #size of tile
SDX=4 #selection frame size
M=3 #match 3(?) game
NOS = (-1, -1) #constant to indicate clear selection
FALL_S=0.2 #speed of fall per each tile
FALL_T=0 #constant fall tile
IMAGES = ['Cherries', 'Grapes', 'Red_Apple',
		               'Strawberry', 'Melon', 'Peach', 'Chestnut']
		               
SEL_IMAGE = 'White_Square'		       

class Match (Layer):

	def setup(self, gridX, gridY, tileNumber):
		self.GRIDX, self.GRIDY = gridX, gridY
		# This will be called before the first frame is drawn.
		self.images = IMAGES[:tileNumber]
		self.scoreLayers=[]
		self.selLayer = Layer(Rect(0, 0, TILE_SIZE+2*SDX, TILE_SIZE+2*SDX))
		self.selLayer.alpha = 0
		self.selLayer.image = SEL_IMAGE
		self.add_layer(self.selLayer)
		
		self.score = 0
		self.selection = (-1, -1)
		self.tint = (-1, -1)
		self.animationCount = 0
		self.toCheck = set()
		self.inverse = None 
		
		self.grid = [None for _ in xrange(self.GRIDX*self.GRIDY)]
		self.gameOver = True 
		
		while self.gameOver:
			for y in xrange(self.GRIDY):
				for x in xrange(self.GRIDX):
					bad=True 
					tile = Layer(Rect(x*TILE_SIZE, y*TILE_SIZE, 
					                  TILE_SIZE, TILE_SIZE))
					while bad:
						bad=False 
						tile.image = choice(self.images)
						if x>=M-1 and all([self[x-i-1, y].image ==
					                   tile.image for i in xrange(M-1)]):
							bad=True
						if y>=M-1 and all([self[x, y-i-1].image ==
					                   tile.image for i in xrange(M-1)]):
							bad=True
					self[x,y]=tile
			self.gameOver = not self.moveAvailiable()
		
		for tile in self.grid:		
			self.add_layer(tile)
		
	def __getitem__(self, (x, y)):
		return self.grid[x+y*self.GRIDX]
	
	def __setitem__(self, (x, y), img):
		self.grid[x+y*self.GRIDX] = img

	def clampTile(self, x, lim):
		ret = int(x/TILE_SIZE)
		return ret if 0 <= ret < lim else -1

	def touchTile(self, touch):
		return (self.clampTile(touch.location.x-self.frame.x, self.GRIDX), 
		        self.clampTile(touch.location.y-self.frame.y, self.GRIDY))
	
	def touch_began(self, touch):
		self.tint = self.touchTile(touch)

	def touch_moved(self, touch):
		self.tint = self.touchTile(touch)

	def touch_ended(self, touch):
		self.tint = NOS
		if self.animationCount:
			return
		pt = self.touchTile(touch)
		if pt==NOS:
			pass
		elif pt==self.selection:
			sound.play_effect('Click_1')
			pt=NOS
		elif sum([abs(a-b) for a,b in zip(pt, self.selection)])==1:
			if self[pt].image!=self[self.selection].image:
				self.beginSwap(self.selection, pt)
				pt=NOS
			else: 
				sound.play_effect('Click_1')
		else:
			sound.play_effect('Click_1')
		self.selection=pt
		
		if pt!=NOS:
			self.selLayer.frame.x = pt[0]*TILE_SIZE-SDX
			self.selLayer.frame.y = pt[1]*TILE_SIZE-SDX
			self.selLayer.animate('alpha', 0.3, 0.2)
		else: 
			self.selLayer.animate('alpha', 0, 0.2)
			
			
	def beginSwap(self, p1, p2, check=True):
		sound.play_effect('Woosh_1' if check else 'Woosh_2')
		self[p1], self[p2] = self[p2], self[p1]
		self.animationCount += 2
		if check:
			self.inverse = (p1, p2)
			self.toCheck.add(p1)
			self.toCheck.add(p2)
		self[p1].animate('frame', self[p2].frame, completion=self.animMoveDone)
		self[p2].animate('frame', self[p1].frame, completion=self.animMoveDone)

	
	def animMoveDone(self):
		self.animationCount -= 1
		if self.animationCount == 0:
			if self.toCheck and not self.check():
				if self.inverse:
					self.beginSwap(*(self.inverse), check=False )
					self.inverse = None

	def checkTiles(self, toCheck):
		toKill = set()
		killGroups=set()
		directions = [((-1,0), (1,0)), ((0,1), (0,-1))]
		for tile in toCheck:
			for line in directions:
				cur = set()
				for d in line:
					t = tile
					while t and self[tile].image==self[t].image:
						cur.add(t)
						t= tuple( (a+b) for a,b in zip(t, d) )
						t= t if all([0<=a<m for a,m in zip(t,(self.GRIDX,self.GRIDY))]) else None
				if len(cur)>=M:
					toKill.update(cur)
					killGroups.add(tuple(sorted(cur)))
		return toKill, killGroups
	
	
	def check(self):
		self.toKill, killGroups = self.checkTiles(self.toCheck)		
		self.toCheck.clear()
		
		for tile in self.toKill:
			self[tile].animate('alpha', 0, completion=self.animKillDone)
			self.animationCount += 1
		if self.toKill:
			self.inverse=None 
			sound.play_effect('Coin_4')
			print  killGroups
			for sg in killGroups:
				a = map(self.__getitem__, sg)
				a = map(lambda l: getattr(l, 'frame'), a)
				a = map(lambda r: (r.center().x,r.center().y), a)
				l = len(a)
				a = map(sum, zip(*a))
				a = map(lambda p: p/l+randrange(-TILE_SIZE/3,TILE_SIZE/3), a)
				score = TextLayer(str(l), 'ChalkboardSE-Bold', 40)
				score.frame.center(*a)
				self.add_layer(score)
				score.animate('alpha', 0, completion=self.killScores)
				score.animate('frame', Rect(score.frame.x, score.frame.y+50,
				                            score.frame.w, score.frame.h))
				self.scoreLayers.append(score)
				self.score += l
				print('Score: ' + str(self.score))
		return bool(self.toKill)
	
	def killScores(self):
		s = self.scoreLayers.pop(0)
		self.remove_layer(s)
	
	def animKillDone(self):
		self.animationCount -= 1
		if self.animationCount==0:
			for x in xrange(self.GRIDX):
				toTop = []
				ys = sorted([y for xx,y in self.toKill if xx==x])
				if ys:
					for y in xrange(ys[0], self.GRIDY):
						self.toCheck.add((x,y))
					for y in ys:
						toTop.append(self[x,y])
					drop = 0
					for y in xrange(ys[0], self.GRIDY):
						if y in ys:
							drop += 1
						else:
							self[x, y-drop], self[x,y]= self[x,y], self[x, y-drop]
							t=drop*FALL_S+FALL_T
							self[x,y-drop].animate('frame', self[x, y].frame, t,
							                        completion=self.animMoveDone)
							self.animationCount += 1
							self[x, y].frame = Rect(*(self[x,y-drop].frame.as_tuple()))
					for y in xrange(drop):
						c = toTop.pop()
						c.image=choice(self.images)
						t=drop*FALL_S+FALL_T
						c.frame=Rect(x*TILE_SIZE, (y+self.GRIDY)*TILE_SIZE, 
						             TILE_SIZE, TILE_SIZE)
						c.animate('frame', Rect(x*TILE_SIZE, 
						             (self.GRIDY-drop+y)*TILE_SIZE, 
						             TILE_SIZE, TILE_SIZE), t,
						             completion=self.animMoveDone)
						self.animationCount += 1
						c.alpha=1
						self[x,y-drop]=c
			self.toKill.clear()
			if not self.moveAvailiable():
				self.gameOver=True
			
		
	def doesTileHasMoves(self, x, y):
		toKill, _ = self.checkTiles([(x,y)])
		return len(toKill)
		
	def moveAvailiable(self):
		ret = False 
		for y in xrange(self.GRIDY-1):
			for x in xrange(self.GRIDX-1):
				self[x,y], self[x,y+1]=self[x,y+1], self[x,y]
				if self.doesTileHasMoves(x,y):
					ret = True
				if self.doesTileHasMoves(x,y+1):
					ret = True
				self[x,y], self[x,y+1]=self[x,y+1], self[x,y]
				self[x,y], self[x+1,y]=self[x+1,y], self[x,y]
				if self.doesTileHasMoves(x,y):
					ret = True
				if self.doesTileHasMoves(x+1,y):
					ret = True
				self[x,y], self[x+1,y]=self[x+1,y], self[x,y]
				if ret:
					return True 
		return False 
				
class GameScene(Scene):
	MENU, GAME, GAME_OVER = 1, 2, 3
	
	def setup(self):
		for effect in ('Click_1', 'Woosh_1', 'Woosh_2', 'Coin_4'):
			sound.load_effect(effect)
		for i in IMAGES:
			load_image(i)
		load_image(SEL_IMAGE)
		self.root_layer = Layer(self.bounds)
		self.effectsLayer = Layer(self.bounds)
		self.newGame(4, 4, 5)
		
	def newGame(self, xx, yy, nl):
		self.gameLayer = Match(Rect(self.bounds.x, self.bounds.y+100,
		                            xx*TILE_SIZE, yy*TILE_SIZE))
		self.gameLayer.setup(xx, yy, nl)
		self.root_layer.remove_layer(self.effectsLayer)
		self.root_layer.add_layer(self.gameLayer)
		self.root_layer.add_layer(self.effectsLayer)
		self.state = GameScene.GAME
		
	def draw(self):
		background(0, 0.1, 0.2)
		self.root_layer.update(self.dt)
		self.root_layer.draw()
		if self.state==GameScene.GAME:
			if self.gameLayer.gameOver:
				self.gameLayer.animate('alpha', 0, 4.5)
				o = TextLayer("Game Over", 'Helvetica-Bold', 60)
				o.frame.center(self.effectsLayer.frame.center())
				o.alpha = 0
				o.animate('alpha',1,5, completion=self.gameEnd)
				o.animate('scale_x',1.5,2)
				o.animate('scale_y',1.5,2)
				self.effectsLayer.add_layer(o)
				self.state=GameScene.GAME_OVER
			
	def gameEnd(self):
		self.root_layer.remove_layer(self.gameLayer)
		self.gameLayer = None
			
	def touch_began(self, touch):
		if self.gameLayer:
			if touch.location in self.gameLayer.frame:
				self.gameLayer.touch_began(touch)

	def touch_moved(self, touch):
		if self.gameLayer:
			if touch.location in self.gameLayer.frame:
				self.gameLayer.touch_moved(touch)

	def touch_ended(self, touch):
		if self.gameLayer:
			if touch.location in self.gameLayer.frame:
				self.gameLayer.touch_ended(touch)
		else:
			for f in list(self.effectsLayer.sublayers):
				self.effectsLayer.remove_layer(f)
			self.newGame(5,5,5)
 
run(GameScene(), PORTRAIT)
