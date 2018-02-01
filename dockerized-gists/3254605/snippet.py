import random
import sys

import pygame
from pygame.locals import *

num = 0

def win():
    pygame.display.set_mode((2048, 480))
    screen = pygame.display.get_surface()
    font = pygame.font.Font(pygame.font.get_default_font(), 480)
    new = font.render("YOU WIN", True, (0,0,0), (255,255,255))
    screen.blit(new, (0,0))
    pygame.display.flip()
    return True

def switch(num=0):
    screen = pygame.display.get_surface()
    font = pygame.font.Font(pygame.font.get_default_font(), 480)
    new = font.render("{0}".format(num), True, (0,0,0), (255,255,255))
    screen.blit(new, (0,0))
    pygame.display.flip()

    if random.randint(0, 1000) == 26:
        return win()
    return False

def input(events, care):
    global num
    for event in events:
        if event.type == QUIT:
            sys.exit(0)
        elif event.type == KEYDOWN and not care:
            num = int(not bool(num))
            return switch(num)
    return care


pygame.init()
pygame.display.set_mode((260, 480))
pygame.display.set_caption("0")
switch()

winned = False
while True:
    winned = input(pygame.event.get(), winned)
    print winned