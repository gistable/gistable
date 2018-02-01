#in the name of god
#Amirreza salimi && biatosite15@gmail.com
import sys
import time
import os

class gf(object):
	def __init__(self,ch):
		super(gf, self).__init__()
		self.w=100
		self.h=100
		self.ch=ch
		self.obj={}
		self.d=[]
		self.cr(self.w,self.h)
	def cr(self,w,h):
		self.d=[]
		self.d=[[self.ch for x in range(w)] for y in range(h)]

	def setWin(self,w,h):
		self.w=w
		self.h=h
		self.cr(w,h)
	def show(self):
		b=''
		for x in range(self.w):
			for y in range(self.h):
				b+=str(self.d[x][y])
			b+='\n'	
		return b
 
	def clear(self):
		os.system('cls' if os.name=='nt' else 'clear')

	def run(self,s,f):
		while True:
			self.clear()
			print self.show()
			f()
			time.sleep(s)
	def pix(self,x,y,c):
		self.d[x][y]=c		
    
#examples & functions
g=gf(' ')
g.setWin(22,22) # width,height
 
def text(t,l,s):
	for i in range(len(t)):
		g.pix(l,i+s,t[i])

text("hello world !",1,3)

def layout():
	n=0
	for x in range(20):
		for y in range(20):
			if x==0 or y==0 or x==19 or y==19:
				g.pix(x,y,"#")
#draw a '#' border for layout
layout()

u=0
def r():
	global u
	u += 1
	text(" timer : %s"%u,4,1)
 
g.run(.100,r)
input("")