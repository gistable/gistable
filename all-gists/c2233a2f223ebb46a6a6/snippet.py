import math
import turtle as t
p1 = t.Turtle()
p1.left(70)
p1.speed=9
p1.dx = math.cos(p1.heading()*math.pi/180)*p1.speed
p1.dy = math.sin(p1.heading()*math.pi/180)*p1.speed
for step in range(100):
	x = p1.xcor()
	y = p1.ycor()
	p1.dy -= 0.1
	x += p1.dx
	y += p1.dy
	p1.goto(x,y)
t.exitonclick()