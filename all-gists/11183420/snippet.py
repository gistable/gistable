#!/usr/bin/env python

import turtle

D = 90
L = 10

def iterate(axiom, num=0, initator='F'):
    """
    Compute turtle rule string by iterating on an axiom
    """

    def translate(current, axiom):
        """
        Translate all the "F" with the axiom for current string
        """
        result = ''
        consts = {'+', '-', '[', ']'}
        for c in current:
            if c in consts:
                result += c
                continue
            if c == 'F':
                result += axiom
        return result

    # Set initator
    result = initator
    for i in xrange(0, num):
        # For ever iteration, translate the rule string
        result = translate(result, axiom)
    return result

def draw(axiom, d=D, l=L):
    """
    Use turtle to draw the L-System
    """
    stack  = []                 # For tracking turtle positions
    screen = turtle.Screen()
    alex   = turtle.Turtle()

    alex.hideturtle()           # Don't show the turtle
    alex.speed(0)               # Make the turtle faster
    alex.left(90)               # Point up instead of right

    for i in xrange(len(axiom)):
        c = axiom[i]

        if c == 'F':
            alex.forward(l)

        if c == 'f':
            alex.penup()
            alex.forward(l)
            alex.pendown()

        if c == '+':
            alex.left(d)

        if c == '-':
            alex.right(d)

        if c == '[':
            stack.append((alex.heading(), alex.pos()))

        if c == ']':
            heading, position = stack.pop()
            alex.penup()
            alex.goto(position)
            alex.setheading(heading)
            alex.pendown()

    screen.onkey(screen.bye, 'q')
    screen.listen()
    turtle.mainloop()

if __name__ == '__main__':

    axiom = "F-F+F+FF-F-F+F"
    axiom = iterate(axiom, 3, "F-F-F-F")
    draw(axiom, 90, 2)
