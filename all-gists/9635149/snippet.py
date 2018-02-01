import os,tty;tty.setcbreak(0);M=['']*16
def G(v):
 p=['']*4;u=list(filter(str,v));i=3
 while u:z=u.pop();p[i]=u and z==u[-1]and 2*u.pop()or z;i-=1
 return p
def Y(M,k):i=1;M=zip(*[iter(M)]*4);exec'M=map([list,G][i*k==k*k],zip(*M))[::-1];i+=1;'*4;return sum(M,[])
while 1:
 r=id(M)%71+17
 while M[r%16]*r:r-=1
 if r:M[r%16]=r%7%2*2+2
 J="WIN"*(2048in M)or"LOSE"*all(Y(M,0));print'\x1b[2J\x1b[H'+('%4s|'*4+'\n')*4%tuple(M)+J
 if J:break
 M=Y(M,">BDAC".find(os.read(0,3)[2]))