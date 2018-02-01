from scryptos import *

p1 = 32581479300404876772405716877547
p2 = 27038194053540661979045656526063
p3 = 26440615366395242196516853423447
n = p1*p2*p3
e = 3

c = int(open("flag.enc", "rb").read().encode("hex"), 16)

# from User's Guide to PARI/GP, nth_root function
sqrtnall = 'sqrtnall(x,n)={my(V,r,z,r2);r=sqrtn(x,n,&z);if(!z,error("Impossible case in sqrtn"));if(type(x)=="t_INTMOD"||type(x)=="t_PADIC",r2 = r*z;n=1;while(r2!=r,r2*=z;n++));V=vector(n);V[1]=r;for(i=2,n,V[i]=V[i-1]*z);V}'

c1 = eval(parigp([sqrtnall, "Vec(liftall(sqrtnall(Mod(%d, %d), 3)))" % (c, p1)]))
c2 = eval(parigp([sqrtnall, "Vec(liftall(sqrtnall(Mod(%d, %d), 3)))" % (c, p2)]))
c3 = eval(parigp([sqrtnall, "Vec(liftall(sqrtnall(Mod(%d, %d), 3)))" % (c, p3)]))

"""
c1 = [6149264605288583791069539134541, 13404203109409336045283549715377, 13028011585706956936052628027629]
c2 = [19616973567618515464515107624812]
c3 = [13374868592866626517389128266735, 7379361747422713811654086477766, 5686385026105901867473638678946]
"""

for x in c1:
  for y in c2:
    for z in c3:
      crt = chinese_remainder_theorem([(x, p1), (y, p2), (z, p3)])
      d = hex(crt, 2)[2:].decode("hex")
      if "0ctf" in d:
        print d[d.find("0ctf"):].strip()
