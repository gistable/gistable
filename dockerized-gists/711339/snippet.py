#! /usr/bin/env python
import sys,os,math,pygame,random,pprint
bwpx,bhpx,score,bw,bh,board,tickcnt,TICK=0,0,0,10,20,[],0,pygame.USEREVENT + 1
cmap={'A':(255,0,0),'B':(0,255,0),'C':(0,0,255),'D':(255,255,0),'E':(0,255,55),'F':(128,255,0),' ':(0,0,0)}
pieces,piece,px,py=['AAAA',' B \nBBB','CC \n CC',' DD\nDD ','EE\nE \nE ','FF\nFF'],None,0,0

def render():
   for i in range(bh):
      for j in range(bw):
         if i in range(py,py+len(piece.split('\n'))) and j in range(px,px+len(piece.split('\n')[0])):
            c=cmap[piece.split('\n')[i-py][j-px]]
         else: c=cmap[board[i][j]]
         pygame.draw.rect(screen,c,((j*bwpx,i*bhpx),(bwpx,bhpx)))
   pygame.display.flip()

def tick():
   global piece,px,py,tickcnt
   keys=pygame.key.get_pressed()
   if keys[pygame.K_LEFT]:
      if px > 0: px-=1
   if keys[pygame.K_RIGHT]:
      if px+len(piece.split('\n')[0]) < bw: px+=1
   if keys[pygame.K_SPACE]: py=drop_piece(piece,px,py)
   if keys[pygame.K_RETURN]: piece = rotate_piece(piece)
   if tickcnt%5==0:
      if collide_piece(piece,px,py+1):
         if py==0:
            print "GAME OVER: score %i"%score
            sys.exit()
         fix_piece(piece,px,py)
         next_piece()
      else: py+=1
      chk_board()
   tickcnt += 1

def next_piece():
   global piece,px,py
   piece=str(pieces[random.randint(0,len(pieces)-1)])
   px=bw/2-len(piece.split('\n')[0])/2
   py=0

def rotate_piece(p):
   pp,pl="",p.split('\n')
   for i in range(len(pl)*len(pl[0])):
      pp+=pl[len(pl)-1-i%len(pl)][i/len(pl)]
      if i%len(pl)==len(pl)-1: pp+='\n' 
   return pp.rstrip('\n')

def drop_piece(p,x,y):
   ph = len(p.split('\n'))
   while y <= bh-ph:
      if collide_piece(p,x,y+1): break
      y += 1
   return y 

def collide_piece(p,x,y):
   pl=p.split('\n')
   if y+len(pl) >= len(board): return True
   for i in range(len(pl)):
      for j in range(len(pl[0])):
         if pl[i][j] != ' ' and board[i+y][j+x] != ' ':
            return True
   return False 

def fix_piece(piece,x,y):
   global board
   pl=piece.split('\n')
   for i in range(len(pl)):
      for j in range(len(pl[0])):
         if pl[i][j] != ' ': board[i+y]=board[i+y][0:j+x]+pl[i][j]+board[i+y][j+x+1:]

def chk_board():
   global board,score
   nboard,iar=[],0
   for i in range(bh-1,0,-1):
      if board[i].find(" ") < 0: iar+=1
      else:
         if iar > 0: score += 2**iar
         nboard.append(board[i])
         iar=0
   while len(nboard) < bh: nboard.append(" "*bw)
   nboard.reverse()
   board=nboard

pygame.init()
size = width, height = 400, 800
screen = pygame.display.set_mode(size)
f1 = pygame.font.SysFont("Arial",12)
board=[" "*bw for i in range(bh)]
bwpx,bhpx=int(screen.get_width()/bw),int(screen.get_height()/bh)
pygame.display.update()
pygame.time.set_timer(TICK,100)
next_piece()
render()
while 1:
   event = pygame.event.wait()
   if event.type == pygame.QUIT: 
      sys.exit()
   elif event.type == TICK:
      render()
      tick()
