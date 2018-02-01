#!/usr/bin/python3

import turtle

#the number of digits to use
numDigits = 1000000
changeColorInc = numDigits / 10
colors = iter(["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#551A8B"])
#scale = 0.99 1k
#scale = 0.199#10k
#scale = 0.025#100k
scale = 0.01#1million
filename = "prime1mill.eps"

canvas = turtle.Screen()
canvas.setup(width=1000, height=1000, startx=None, starty=None)

def draw_background(a_turtle):
    """ Draw a background rectangle. """
    ts = a_turtle.getscreen()
    canvas = ts.getcanvas()
    height = ts.getcanvas()._canvas.winfo_height()
    width = ts.getcanvas()._canvas.winfo_width()

    turtleheading = bob.heading()
    turtlespeed = bob.speed()
    penposn = bob.position()
    penstate = bob.pen()

    bob.penup()
    bob.speed(0)  # fastest
    bob.goto(-width/2-2, -height/2+3)
    bob.fillcolor(turtle.Screen().bgcolor())
    bob.begin_fill()
    bob.setheading(0)
    bob.forward(width)
    bob.setheading(90)
    bob.forward(height)
    bob.setheading(180)
    bob.forward(width)
    bob.setheading(270)
    bob.forward(height)
    bob.end_fill()

    bob.penup()
    bob.setposition(*penposn)
    bob.pen(penstate)
    bob.setheading(turtleheading)
    bob.speed(turtlespeed)
    

def getPrimeDigits():
	#0.12345678910111213…
	current = 1;
	newP =next_prime(current)
#	print(newP)
	while True:
		newP =next_prime(current)
#		print(newP)
		current_str = str(newP);
#		currentPrime =current_str
		for digit in current_str:
			yield int(digit)
		current = newP + 1
        
def getDigits():
	#0.12345678910111213…
	current = 1;
	while True:
		current_str = str(current);
		for digit in current_str:
			yield int(digit)
		current = current + 1

#gen = getDigits()
gen = getPrimeDigits()
#ts = turtle.Turtle()
#ts = turtle.getscreen()

s = turtle.Screen()
s.bgcolor("black")

bob = turtle.Turtle()
draw_background(bob)

ts = bob.getscreen()
canvas = ts.getcanvas()

turtle.hideturtle()
turtle.speed(0)
turtle.tracer(0,0)

#canvas.bgcolor("orange")

#bob = turtle.Turtle()
draw_background(bob)

turtle.penup()
#turtle.setpos(-300,400)

#turtle.setpos(-100,100)#1k 

turtle.setpos(-400,400)

#turtle.forward(-450)
#turtle.left(90)
#turtle.forward(100)
turtle.pendown()
turtle.pensize(2)
for i in range(numDigits):
	digit = next(gen)
	if i % changeColorInc == 0:
		turtle.pencolor(next(colors))
	angle = digit * 36
	turtle.right(angle)
	turtle.forward(1 * scale)
	turtle.left(angle)

turtle.update()

ts.getcanvas().postscript(file=filename)
print(ts.bgcolor())
turtle.bye()