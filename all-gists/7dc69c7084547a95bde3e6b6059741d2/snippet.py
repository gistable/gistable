import turtle
t=turtle.Pen()
def square(x):
        t.forward(x)
        t.left(90)
        t.forward(x)
        t.left(90)
        t.forward(x)
        t.left(90)
        t.forward(x)
        t.left(90)
def circle(x):
        for i in range(0,360):
                t.forward(x)
                t.left(1)
def quadrilateral(w,x,y,z,a,b,c,d):
        t.forward(w)
        t.left(a)
        t.forward(x)
        t.left(b)
        t.forward(y)
        t.left(c)
        t.forward(z)
        t.left(d)
def polygon(a,b,c):
        x=0
        while x!=a:
                t.forward(b)
                t.left(c)
                x+=1
def triangle(x,y,z,a,b,c):
        a=180-a
        b=180-b
        c=180-c
        t.forward(x)
        t.left(a)
        t.forward(y)
        t.left(b)
        t.forward(z)
        t.left(c)
