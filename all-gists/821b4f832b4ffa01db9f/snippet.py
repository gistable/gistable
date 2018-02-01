class Game2048(object):
 def __init__(self, s):self.s = s
 def input(self, d):
  from itertools import product as b;import random as h
  e,f,z,w=[0,1,0,-1],[1,0,-1,0],range,len;r=z(4);g=b(r,r)
  t=[(x,y)for x,y in g if not(0<=x-e[d]<4and 0<=y-f[d]<4)]
  for (x,y),s in zip(t,[self.s]*w(t)):
   l,k=[v for v in[s[x+i*e[d]][y+i*f[d]]for i in r]if v],[]
   for i,g,a in zip(z(w(l)),[b(r,r)]*w(l),[h.choice]*w(l)):
    k+=((i<w(l)-1and l[i]==l[i+1])and(i==0 or not k[i-1]),)
   c=[(k[i]+1)*l[i]for i in z(w(l))if(i==0 or not k[i-1])]
   for i in r:s[x+i*e[d]][y+i*f[d]]=c[i]if i<len(c)else 0
  p,q=a([(x,y)for x,y in g if s[x][y]<1]);s[p][q]=a([2,4])