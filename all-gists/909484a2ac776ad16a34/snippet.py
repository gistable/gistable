# 2048.py
# Written in python / pygame by DavidSousaRJ - david.sousarj@gmail.com
# License: Creative Commons
# Sorry about some comments in portuguese!
import os
import sys
import pygame
from pygame.locals import *
from random import randint

TABLE = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]


def isgameover(TABLE):
    status = 0
    zerocount = 0
    for LINE in TABLE:
        if 2048 in LINE:
            status = 1
            return status
        elif 0 not in LINE:
            zerocount += 1
    if zerocount == 4:
        # condicoes de gameover: nao ter zero e nao ter consecutivo igual
        # procura consecutivos horizontal
        for i in range(4):
            for j in range(3):
                if TABLE[i][j] == TABLE[i][j + 1]:
                    return status
        # procura consecutivos na vertical
        for j in range(4):
            for i in range(3):
                if TABLE[i][j] == TABLE[i + 1][j]:
                    return status
        status = 2
    return status

# regras do 2048
# define a direcaoo jogada, p.ex. : cima
# para cada coluna, de cima pra baixo
# move o numero para o zero-consecutivo-mais-longe
# se o nao-zero-mais-perto e igual ao numero, combina


def moveup(pi, pj, T):
    justcomb = False
    while pi > 0 and (T[pi - 1][pj] == 0 or
                      (T[pi - 1][pj] == T[pi][pj] and not justcomb)):
        if T[pi - 1][pj] == 0:
            T[pi - 1][pj] = T[pi][pj]
            T[pi][pj] = 0
            pi -= 1
        elif T[pi - 1][pj] == T[pi][pj]:
            T[pi - 1][pj] += T[pi][pj]
            T[pi][pj] = 0
            pi -= 1
            justcomb = True
    return T


def movedown(pi, pj, T):
    justcomb = False
    while pi < 3 and (T[pi + 1][pj] == 0 or
                      (T[pi + 1][pj] == T[pi][pj] and not justcomb)):
        if T[pi + 1][pj] == 0:
            T[pi + 1][pj] = T[pi][pj]
            T[pi][pj] = 0
            pi += 1
        elif T[pi + 1][pj] == T[pi][pj]:
            T[pi + 1][pj] += T[pi][pj]
            T[pi][pj] = 0
            pi += 1
            justcomb = True
    return T


def moveleft(pi, pj, T):
    justcomb = False
    while pj > 0 and (T[pi][pj - 1] == 0 or
                      (T[pi][pj - 1] == T[pi][pj] and not justcomb)):
        if T[pi][pj - 1] == 0:
            T[pi][pj - 1] = T[pi][pj]
            T[pi][pj] = 0
            pj -= 1
        elif T[pi][pj - 1] == T[pi][pj]:
            T[pi][pj - 1] += T[pi][pj]
            T[pi][pj] = 0
            pj -= 1
            justcomb = True
    return T


def moveright(pi, pj, T):
    justcomb = False
    while pj < 3 and (T[pi][pj + 1] == 0 or
                      (T[pi][pj + 1] == T[pi][pj] and not justcomb)):
        if T[pi][pj + 1] == 0:
            T[pi][pj + 1] = T[pi][pj]
            T[pi][pj] = 0
            pj += 1
        elif T[pi][pj + 1] == T[pi][pj]:
            T[pi][pj + 1] += T[pi][pj]
            T[pi][pj] = 0
            pj += 1
            justcomb = True
    return T


def randomfill(TABLE):
    # search for zero in the game table
    flatTABLE = sum(TABLE, [])
    if 0 not in flatTABLE:
        return TABLE
    empty = False
    w = 0
    while not empty:
        w = randint(0, 15)
        if TABLE[w // 4][w % 4] == 0:
            empty = True
    z = randint(1, 5)
    if z == 5:
        TABLE[w // 4][w % 4] = 4
    else:
        TABLE[w // 4][w % 4] = 2
    return TABLE


def key(DIRECTION, TABLE):
    if DIRECTION == 'w':
        for pi in range(1, 4):
            for pj in range(4):
                if TABLE[pi][pj] != 0:
                    TABLE = moveup(pi, pj, TABLE)
    elif DIRECTION == 's':
        for pi in range(2, -1, -1):
            for pj in range(4):
                if TABLE[pi][pj] != 0:
                    TABLE = movedown(pi, pj, TABLE)
    elif DIRECTION == 'a':
        for pj in range(1, 4):
            for pi in range(4):
                if TABLE[pi][pj] != 0:
                    TABLE = moveleft(pi, pj, TABLE)
    elif DIRECTION == 'd':
        for pj in range(2, -1, -1):
            for pi in range(4):
                if TABLE[pi][pj] != 0:
                    TABLE = moveright(pi, pj, TABLE)
    return TABLE


def showtext(TABLE):
    os.system('clear')
    for LINE in TABLE:
        for N in LINE:
            print("%4s" % N, end=' ')
        print("")

########################################################################
# Parte Grafica
width = 400
height = 400
boxsize = min(width, height) // 4
margin = 5
thickness = 0
STATUS = 0

color1 = (100, 100, 100)
color2 = (200, 200, 200)

dictcolor = {
    0: color2,
    2: (150, 150, 150),
    4: (180, 180, 180),
    8: (255, 200, 200),
    16: (255, 100, 100),
    32: (255, 50, 50),
    64: (255, 0, 0),
    128: (255, 255, 50),
    256: (255, 255, 100),
    512: (255, 255, 150),
    1024: (255, 255, 200),
    2048: (255, 255, 255)}

# Init screen
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Python 2048 by DavidSousaRJ')
myfont = pygame.font.SysFont("Impact", 30)


def gameover(STATUS):
    if STATUS == 1:
        label = myfont.render("You win! :)", 1, (255, 255, 255))
        screen.blit(label, (100, 100))
    elif STATUS == 2:
        label = myfont.render("Game over! :(", 1, (255, 255, 255))
        screen.blit(label, (100, 100))
    pygame.display.update()


def show(TABLE):
    screen.fill(color1)
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(screen, dictcolor[TABLE[i][j]],
                             (j * boxsize + margin,
                              i * boxsize +
                              margin,
                              boxsize - 2 *
                              margin,
                              boxsize - 2 * margin),
                             thickness)
            if TABLE[i][j] != 0:
                label = myfont.render(
                    "%4s" % (TABLE[i][j]), 1, (255, 255, 255))
                screen.blit(
                    label, (j * boxsize + 4 * margin,
                            i * boxsize + 5 * margin))
    pygame.display.update()


# paintCanvas
TABLE = randomfill(TABLE)
TABLE = randomfill(TABLE)
show(TABLE)
showtext(TABLE)
running = True

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            print("quit")
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if running:
                if event.key == pygame.K_UP:
                    TABLE = key('w', TABLE)
                    TABLE = randomfill(TABLE)
                    show(TABLE)
                    showtext(TABLE)
                    STATUS = isgameover(TABLE)
                    if STATUS < 0:
                        running = False
                        gameover(STATUS)
                if event.key == pygame.K_DOWN:
                    TABLE = key('s', TABLE)
                    TABLE = randomfill(TABLE)
                    show(TABLE)
                    showtext(TABLE)
                    STATUS = isgameover(TABLE)
                    if STATUS < 0:
                        running = False
                        gameover(STATUS)
                if event.key == pygame.K_LEFT:
                    TABLE = key('a', TABLE)
                    TABLE = randomfill(TABLE)
                    show(TABLE)
                    showtext(TABLE)
                    STATUS = isgameover(TABLE)
                    if STATUS < 0:
                        running = False
                        gameover(STATUS)
                if event.key == pygame.K_RIGHT:
                    TABLE = key('d', TABLE)
                    TABLE = randomfill(TABLE)
                    show(TABLE)
                    showtext(TABLE)
                    STATUS = isgameover(TABLE)
                    if STATUS < 0:
                        running = False
                        gameover(STATUS)
# end
