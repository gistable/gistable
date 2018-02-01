# coding: utf-8

import pygame
import random

rr = random.randrange 
SIZE = 800, 600
cellsize = 20

try:
    range = xrange
except NameError:
    pass

def init():
    global SCREEN
    SCREEN = pygame.display.set_mode((SIZE))
    

class Grid(object):
    
    def __init__(self):
        self.width = SIZE[0] / cellsize
        self.height = SIZE[1] / cellsize
        self.grid = self.makegrid()
        self.color = (255, 200, 200)
        
    def makegrid(self):
        return [ [0, ] * self.height for y in range(self.width)   ]
        
    def populate(self, n):
        for i in range(n):
            x, y = rr(0, self.width), rr(0, self.height)
            self[x, y] = True
    
    def __getitem__(self, pos):
        if pos[0] < 0 or pos[1] < 0:
            return 0
        try:
            return self.grid[pos[0]][pos[1]]
        except IndexError:
            return 0
    
    def __setitem__(self, pos, value):
        self.grid[pos[0]][pos[1]] = value

    def count_neighbours(self, pos):
        x, y = pos
        return sum((self[x - 1, y -1], self[x - 1, y], self[x - 1, y + 1],
                   self[x, y - 1], self[x, y + 1], 
                   self[x + 1, y -1], self[x + 1, y], self[x + 1, y + 1]))
    
    def __iter__(self):
        for x in range(self.width):
            for y in range(self.height):
                yield (x, y), self[x, y]
    
    def update(self):
        new_grid = self.makegrid()
        for pos, value in self:
            v = self.count_neighbours(pos) 
            if v == 3 or (v == 2 and value):
                new_grid[pos[0]] [pos[1]] = 1
        self.grid = new_grid
    
    def draw(self, surf):
        
        for pos, value in self:
            
            pygame.draw.rect(
                surf, self.color if value else (0, 0, 0), 
                (pos[0] * cellsize + 1, pos[1] * cellsize + 1, cellsize - 2, cellsize -2)
            )

class Exit(BaseException):
    pass
    
def main():
    grid = Grid()
    grid.populate(100)
    starting = True
    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == 0x1b):
                raise Exit
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION and any(event.buttons):
                x, y = event.pos
                grid[x // cellsize, y //cellsize] = True
        if not starting:
            grid.update()
        grid.draw(SCREEN)
        pygame.display.flip()
        pygame.time.delay(200)
        starting = False
        
if __name__ == "__main__":
    try:
        init()
        main()
    except Exit:
        print("Normal termination")

    finally:
        pygame.quit()