import pygame, time, random, sys, copy, os
from pygame.locals import *
t2 = 0
nor = 0
pc = [[[1, 1], [1, 1]], [[1, 0], [1, 0], [1, 1]], [[0, 1], [0, 1], [1, 1]], [[1], [1], [1], [1]], [[0, 1, 1], [1, 1, 0]], [[1, 1, 0], [0, 1, 1]], [[1, 1, 1], [0, 1, 0]]]
cols = [(0, 0, 0), (100, 100, 100), (10, 100, 225), (0, 150, 220), (0, 220, 150), (60, 200, 10), (180, 210, 5), (210, 180, 10), (100, 200, 170)]
pygame.init()
pygame.display.set_mode((320, 240))
sk = pygame.display.get_surface()
f = [[1] + [0 for x in range(8)] + [1] for x in range(19)] + [[1 for x in range(10)]]
of = copy.deepcopy(f)
s = 12
brt = Rect((100, 0, s, s))
b = -1
p = []
lc = [-9, 0]
t = 0
bt = 60
pygame.key.set_repeat(200, 100)
rh = 0
cr = []
crs = pygame.Surface((8*s, s))
crs.fill((255, 0, 0))
crs.set_alpha(100)
gv = -1
z = pygame.font.Font(pygame.font.get_default_font(), 14)
_ = 0
#pygame.mixer.music.load("t.ogg")
#pygame.mixer.music.play(-1)  
while 1:  
    sk.fill((0, 0, 0))
    _su = z.render("Score " + str(_), 1, (255, 255, 255))
    _rect = _su.get_rect()
    _rect.bottomright = (310, 230)
    sk.blit(_su, _rect)  
    if gv >- 1:  
        b = 10
        rh = 0  
        if not t%5:  
            gv -= 1
            f[9 - gv] = [1]*10
            f[10 + gv] = [1]*10
            t = 1  
        if gv == 0:
            gv = 99  
    if b < -1:  
        b += 1  
    if b == -1:  
        b = random.randint(0, 6)
        p = pc[b]
        lc = [5 - len(p)/2, 0]  
    if not t%bt or rh:  
        op = [p[:], lc[:]]
        lc[1]  += 1  
    if b < 0:
        continue  
    rx = 0
    c = 0  
    for l in p:  
        r = 0  
        for k in l:  
            while c + lc[0] < 1:  
                lc[0] += 1  
            while c + lc[0] > 8:  
                lc[0] -= 1  
            if f[r + lc[1]][c + lc[0]] and k:  
                if lc[1] == 0:
                    gv = 10  
                rx = 1  
            r += 1  
        c += 1  
    if rx and not nor:  
        p, lc = op
        c = 0  
        for l in p:  
            r = 0  
            for k in l:  
                if k:  
                    f[r + lc[1]][c + lc[0]] = b + 2  
                r += 1  
            c += 1  
        b = -20
        t = 1
        rx = 0
        rh = 0
        p = []  
    nor  =  False  
    if rh:
        continue  
    for r in f[:-1]:  
        if not r.count(0):  
            wr = r  
            cr += [[f.index(wr), 200]]  
            f.remove(wr)  
            f = [[1] + [0 for x in range(8)] + [1]] + f  
            if gv == -1:  
                _ += 10
                bt = max(8, bt - 1)  
    if gv > -1:
        f = copy.deepcopy(of)  
    c = 0  
    for l in f:  
        r = 0  
        for k in l:  
            try:  
                if r >= lc[0] and c >= lc[1] and p[r - lc[0]][c - lc[1]]:
                    k = b + 2  
            except:
                pass  
            sk.fill([x*0.75 for x in cols[k]], brt.move(r*s, c*s))
            sk.fill(cols[k], brt.move(r*s, c*s).inflate(-4, -4))
            r += 1  
        c += 1  
    for r in cr:  
        crs.set_alpha(r[1])
        sk.blit(crs, (100 + s, r[0]*s))
        cp = cr.index(r)
        cr[cp][-1] -= 5  
        if cr[cp][-1] <= 0:
            cr.remove(cr[cp])  
    if gv >= 0:  
        gs = z.render("GAME OVER", 1, (255, 255, 255))
        gr = gs.get_rect()
        gr.center = (160, 120)
        sk.blit(gs, gr)  
        if gv == 99:
            pygame.display.flip()
            time.sleep(4)
            print "Your score was", _
            sys.exit(0)  
    pygame.display.flip()
    t += 1
    t2 += 1
    time.sleep(0.01)  
    if gv >= 0:
        continue  
    for e in pygame.event.get():  
        if e.type == KEYDOWN:  
            if e.key == K_LEFT:
                op = [p[:], lc[:]]
                lc[0] -= 1  
            if e.key == K_RIGHT:
                op = [p[:], lc[:]]
                lc[0] += 1  
            if e.key == K_DOWN:
                op = [p[:], lc[:]]
                lc[1] += 1
                t = 1  
            if e.key == K_UP and p:
                op = [p[:], lc[:]]
                p=[[p[x][-y - 1] for x in range(len(p))] for y in range(len(p[0]))]
                nor = 1  
            if e.key == K_SPACE:
                rh = 1
