# -*- coding:utf-8 -*-
import pygame
from pygame.locals import *
import pygame.mixer
import sys
import copy
import array

sounds = [0 for j in range(0,20)]
cell = [[0 for j in range(0,20)] for i in range(0,20)]

#Initialize Pygame
def init():
    def sound_init():
        for i in range(0,18):
            sounds[i] = pygame.mixer.Sound("src/" + str(i) + ".wav")
    pygame.init()
    pygame.mixer.init()
    sound_init()
    screen = pygame.display.set_mode((320,320))
    pygame.display.set_caption(u"Life Music")
    screen.fill((0,0,0))
    return screen

#Draw DisPlay
def draw_display(screen,step):
        screen.fill((0,0,0))
        pygame.draw.rect(screen,(0,0,0),Rect(0,0,320,320))
        #Cell Draw
        for i in range(20):
            pygame.draw.line(screen,(255,255,255),(i * 16,0),(i*16,320))
        for j in range(20):
            pygame.draw.line(screen,(255,255,255),(0,j*16),(320,j*16))
        #Line Draw
        pygame.draw.rect(screen,(255,255,0),Rect(step * 16,0,16,320))
        for j in range(20):
            for i in range(20):
                if cell[i][j] == 1:
                    pygame.draw.rect(screen,(0,255,255),Rect(i * 16,j * 16,16,16))
                elif cell[i][j] == 2:
                    pygame.draw.rect(screen,(255,0,0),Rect(i * 16,j * 16,16,16))
        pygame.display.update()

#Cell Result
def cell_result():
    global cell
    next_cell = [[0 for j in range(0,20)] for i in range(0,20)]
    for j in range(20):
        for i in range(20):
            neight_cell = -1 if cell[i][j] else 0
            for c_i in range(-1,2):
                for c_j in range(-1,2):
                    c_i = c_i if i + c_i < 20 else 0
                    c_j = c_j if j + c_j < 20 else 0
                    if cell[i + c_i][j + c_j] > 0:
                        neight_cell += 1
            if neight_cell == 3:
                next_cell[i][j] = 1
            if neight_cell == 2 or cell[i][j] == 2:
                next_cell[i][j] = copy.copy(cell[i][j])
    cell = next_cell

def cell_sound(step):
    for i in range(20):
        if cell[step][i] > 0 and sounds[i] is not 0:sounds[i].play()

#MainLoop
def mainloop(screen):
    SET_FPS = pygame.time.Clock()
    step = 0
    is_run = False
    while True:
        SET_FPS.tick(15)
        if is_run:
            step = 0 if step + 1> 19 else step + 1
            cell_result()
        cell_sound(step)
        draw_display(screen,step)
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                x,y = event.pos
                cell[x/16][y/16] = 1 if cell[x/16][y/16] == 0 else 2 if cell[x/16][y/16] == 1 else 0
                print x/16,y/16
            if event.type == KEYDOWN:
                if (event.key == K_SPACE):
                    is_run = not is_run
                    print is_run
                elif (event.key == K_ESCAPE):
                    sys.exit()
            if event.type == QUIT:
                sys.exit()

def main():
    mainloop(init())

if __name__ == "__main__": main()
