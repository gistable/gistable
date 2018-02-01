import struct
print( 8 * struct.calcsize("P"))
import pygame
from pygame import *
from player import Player
controls=[False, False, False, False]
screen = pygame.display.set_mode((640, 400))
running = 1
player=Player("player.png", [100,150])
while running:
	player.update()
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			running = 0
		if event.type == KEYDOWN:
			if event.key==K_w and player.onGround:
				player.vspeed=-10
			if event.key==K_a:
				controls[1]=True
			if event.key==K_d:
				controls[3]=True
		if event.type == KEYUP:
			if event.key==K_a:
				controls[1]=False
			if event.key==K_d:
				controls[3]=False
	player.move(False, controls[1],False, controls[3])
	screen.fill((100, 127, 180))
	screen.blit(player.image, player.position)
	pygame.display.flip()