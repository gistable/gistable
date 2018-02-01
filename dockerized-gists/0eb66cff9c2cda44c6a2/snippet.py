import pygame

class Button(pygame.sprite.Sprite):
	def __init__(self,text,x,y,width=100,height=100,color=[230,230,230]):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.image.fill(color)
		font_size = int(width//len(text))
		myFont=pygame.font.SysFont("Calibri",font_size)
		myText = myFont.render(text, 1, (0,0,0))
		self.image.blit(myText,(width/2-width/4,height/2-height/4))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
	def pressed(self, mouse):
		if mouse[0] > self.rect.topleft[0]:
			if mouse[1] > self.rect.topleft[1]:
				if mouse[0] < self.rect.bottomright[0]:
					if mouse[1] < self.rect.bottomright[1]:
						return True
					else: return False
				else: return False
			else: return False
		else: return False