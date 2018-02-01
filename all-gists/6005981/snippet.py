import pygame
import random
import math

from vec import Vec
from GF2 import *

pygame.init()

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("lights OUT!")

done = False
is_blue = True

size_x = 5
size_y = 5

rect_width = screen_width / size_x
rect_height = screen_height / size_y

coords = { (x,y) for x in range(size_x) for y in range (size_y) }
lights = Vec (coords, {})

def getRect(margin, x,y):
        left = x * rect_width + margin/2
        top = y * rect_height + margin/2
        return pygame.Rect(left, top, rect_width - margin, rect_height - margin)

def getCoords(sx, sy):
        x = math.floor(sx / rect_width)
        y = math.floor(sy / rect_height)
        return (x,y)

def inBounds(x,y):
        return x >= 0 and x < size_x and y >= 0 and y < size_y

def getEnv(x,y):
        env = [(x,y), (x-1,y), (x+1,y), (x,y-1), (x,y+1)]
        return ((x,y) for (x,y) in env if inBounds(x,y))

def isLightOn(x,y):
        return lights[(x,y)] == one

def switchLight(x,y):
        lights[(x,y)] = one - lights[(x,y)]

def clickOn(x,y):
        for (a,b) in getEnv(x,y):
                switchLight(a,b)

def drawLight (x,y):
        grey = (10,10,10)
        color = (100,10,10)
        if isLightOn(x,y): color = (10, 250, 10)
        pygame.draw.rect(screen, grey, getRect(2, x,y), 0)
        pygame.draw.ellipse(screen, color, getRect(8, x,y), 0)

def drawLights():
        for (x,y) in coords:
                drawLight(x,y)

def randomizeLights():
        random.seed()
        cs = list(coords)
        for i in range(2 * size_x):
                (x,y) = random.choice(cs)
                clickOn(x,y)

# comment the next line if you want a clean board
randomizeLights()

fpsClock = pygame.time.Clock()

while not done:

        # input
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            done = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        (sx, sy) = pygame.mouse.get_pos()
                        (x,y) = getCoords(sx, sy)
                        clickOn (x,y)

        

        # drawing       
        screen.fill((0, 0, 0))
        drawLights()
        
        pygame.display.flip()

        # wait
        fpsClock.tick(60)