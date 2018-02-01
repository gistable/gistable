#!/usr/bin/env python
# -*- coding:utf-8 -*-
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import time
import random

class Snake():
    def __init__(self,length,screen):
        # left top coordinate (y,x)
        self.map = screen
        self.mapY,self.mapX, = self.map.getmaxyx()
        self.hy = random.randrange(length,self.mapY-2-length)
        self.hx = random.randrange(length,self.mapX-2-length)
        self.direction = random.randrange(1,5)
        bodylist = [ 
            [[self.hy+l, self.hx] for l in range(0,length)],
            [[self.hy, self.hx-l] for l in range(0,length)],
            [[self.hy, self.hx+l] for l in range(0,length)],
            [[self.hy-l, self.hx] for l in range(0,length)]            
            ]
        self.body = bodylist[self.direction-1]
        self.length = len(self.body)
        self.head = self.body[0]
        self.headers = ("^", ">", "<", "v") 
        # self.go = random.filter(lambda x: x.STARTswith('go_'),dir(self))[random.randrange(0,4)]
        
        self.turn = self.direction
        self.eat = 0

    def go_up(self):
        self.turn = 1
    def go_right(self):
        self.turn = 2
    def go_left(self):
        self.turn = 3
    def go_down(self):
        self.turn = 4

    def creep(self):
        self.head = self.body[0]
        if self.direction + self.turn != 5:
            self.direction = self.turn
        if self.direction == 1:
            self.target = [self.head[0]-1,self.head[1]]
        if self.direction == 2:
            self.target = [self.head[0],self.head[1]+1]
        if self.direction == 3:
            self.target = [self.head[0],self.head[1]-1]
        if self.direction == 4:
            self.target = [self.head[0]+1,self.head[1]]

    def go(self):
        if not self.eat:
            self.body.pop()
        self.body = [list(self.target)]+self.body

def randomFood(screen,snake):
    y,x = screen.getmaxyx()
    random.seed()
    while True:
        fy,fx = random.randrange(1,y-1),random.randrange(1,x-1)
        if [fy,fx] not in snake.body:
            break
    return [fy,fx]

def VerticalCenter(screen,elements):
    maxY, maxX = screen.getmaxyx()
    z = len(elements)/2
    y,x = maxY/2-z,maxX/2
    for s in elements:
        screen.addstr(y,x-len(s)/2,s,curses.color_pair(1))
        y+=1

def main(screen):
    # set color
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  #Default
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) #Food
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    #Head
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  #Body
     # game init config
    screen.nodelay(1)
    snake = Snake(4,screen)
    food = randomFood(screen, snake)
    START = 0
    OVER = 0
    PAUSED = 0
    SCORE = 0
    SPEED = 10
    while 1:
        maxY, maxX = screen.getmaxyx()
        # food = [1,maxX-1]
        get = screen.getch()
        # handler input
        if get == 10 and START == 0:
            START = 1
        elif get == ord('p') or get == ord(' ') and START == 1:
            PAUSED = PAUSED^1
            screen.nodelay(PAUSED^1) # input block
        elif get == 27:
            break
        elif get == ord('r') and START == 0:
            screen.nodelay(1)
            snake = Snake(4,screen)
            food = randomFood(screen, snake)
            START = 0
            OVER = 0
            PAUSED = 0
            SCORE = 0
            SPEED = 10
        if PAUSED:
            screen.addstr(maxY-1, 1, "Paused", curses.color_pair(1))
            continue
        if OVER:
            elements = ["YOU GET %d SCORE"%SCORE,"GAME OVER","R to reload","ESC to quit"]
            VerticalCenter(screen,elements)
            START = 0
            screen.nodelay(0) # input block
            continue
        # screnn freshen
        screen.clear()
        screen.border(0)
        # move logic
        if START:
            if get ==  KEY_UP:
                snake.go_up()
            elif get == KEY_DOWN:
                snake.go_down()
            elif get == KEY_LEFT:
                snake.go_left()
            elif get == KEY_RIGHT:
                snake.go_right()
            snake.creep()
            # screen.addstr(0, 0, str(snake.target), curses.color_pair(1))
            # screen.addstr(1, 0, str(snake.body), curses.color_pair(1))
            # eat
            if snake.target == food:
                food = randomFood(screen, snake)
                SCORE += 1
                SPEED += 1
                snake.eat = 1
            elif snake.target in snake.body:
                OVER = 1
                time.sleep(2)
                continue
            else:
                snake.eat = 0
            snake.go()
        else:
            screen.addstr(maxY-1, 1, "Enter to start", curses.color_pair(1))
        #draw food
        screen.addstr(food[0], food[1], "$", curses.color_pair(2))
        # draw snake
        for i,p in enumerate(snake.body):
            sc = snake.headers[snake.direction-1] if i==0 else '#'
            color = 3 if i==0 else 4
            # cross the map
            y,x = p
            if y == 0:
                y = maxY-2
                snake.body[i][0] = y
            if y == maxY-1:
                y = 1
                snake.body[i][0] = y
            if x == 0:
                x = maxX-2
                snake.body[i][1] = x
            if x == maxX-1:
                x = 1
                snake.body[i][1] = x
            screen.addstr(y, x, sc, curses.color_pair(color))
        # draw info or debug info
        # screen.addstr(0, 2, "x:%s y:%s" %(maxX,maxY), curses.color_pair(1))
        # screen.addstr(0, 13, "food:%s" %(str(food)), curses.color_pair(1))
        # screen.addstr(maxY-1, maxX-10, "info:%s" %(str(get)), curses.color_pair(1))
        screen.addstr(0,1,"SCORE:%s" %SCORE,curses.color_pair(1))
        screen.refresh()
        time.sleep(1.0/SPEED)
    # print "you get %s" %SCORE

if __name__ == '__main__':
    curses.wrapper(main)
#https://gist.github.com/sanchitgangwar/2158089
#https://github.com/Vik2015/Python-curses-snake-game/blob/master/snake.py
