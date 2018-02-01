import turtle
import random
random.seed(42)
i=0
#file = open("emil.txt", "r")
#file = open("pi1000000.txt", "r")
file = open("sqrt2.txt", "r")
text=file.read() 
pi = list(text)
pi = list(map(int, pi))

screen = turtle.Turtle()
turtle.clearscreen()

wn = turtle.Screen()        # creates a graphics window
wn.tracer(1000000, 25)
wn.setup (width=7000, height=4500, startx=None, starty=None)
turtle.penup()
turtle.hideturtle()
#turtle.setpos(400,240)#pi
#turtle.setpos(650,330)#e
turtle.setpos(500,-170)#sqrt2
#turtle.setpos(0,330) random
turtle.speed(0)
turtle.down()
turtle.pencolor("#ff0000")
angle=0

while i < 1000000:
    #print(pi[i])
    #angle= (int(float(pi[i])))*36 #quicker to turn string to int at start
    #ran= random.randint(0, 9)
    #angle= ran*36
    angle= pi[i]*36
    #print(angle)
    turtle.right(angle)
    turtle.forward(1)
    j=360-angle
    turtle.right(j)
    if i == 0:
        turtle.pencolor("#a6cee3")
    if i ==100000:
        turtle.pencolor("#1f78b4")
    if i == 200000:
        turtle.pencolor("#b2df8a")
    if i == 300000:
        turtle.pencolor("#33a02c")        
    if i == 400000:
        turtle.pencolor("#fb9a99")  
    if i == 500000:
        turtle.pencolor("#e31a1c")  
    if i == 600000:
        turtle.pencolor("#fdbf6f")  
    if i == 700000:
        turtle.pencolor("#ff7f00")  
    if i == 800000:
        turtle.pencolor("#cab2d6")
    if i == 900000:
        turtle.pencolor("#551A8B")       
        

    i=i+1    



ts = turtle.getscreen()
#ts.getcanvas().postscript(file="randompiMC.eps")
#ts.getcanvas().postscript(file="eMC600k.eps")
ts.getcanvas().postscript(file="sqrt2MC1mil.eps")
#ts.getcanvas().postscript(file="pi1mil.eps")
turtle.bye()

