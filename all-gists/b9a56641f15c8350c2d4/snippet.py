#!/usr/bin/python
# Udacity exercise. Just posted the code here to help anyone who wanted to see the work behind my posted result.
__author__ = 'Michael Rosata mrosata1984@gmail.com'
__package__ = ''

from random import random
import turtle

class TurtleArtist(turtle.Turtle):
    _origin = (0, 0)
    _starts = []
    _level = 1
    _len = 140

    def mark_future_start(self):
        self._starts.append(self.position())

    def clear_all_starts(self):
        self._starts = []
        print('Added a new Start')
        print(self._starts)

    def incrememnt_level(self):
        self._level += 1

    def to_origin(self):
        try:
            if self._origin:
                self.goto(self._origin)
        except AttributeError:
                self.home()

    def triangle(self, ang_step1, ang_step2):
        self.turn_move(ang_step1)
        self.mark_future_start()
        self.turn_move(ang_step2)
        self.to_origin()

    def turn_move(self, angle_dist):
        """Pass in (ang, dist) for turtle to turn and move """
        self.right(angle_dist[0])
        self.forward(angle_dist[1])

    def style(self, color='#009b30', shape='turtle', speed=0.1, pen=(0, 0, 0)):
        self.color(color)
        self.pencolor(pen[0], pen[1], pen[2])
        self.shape(shape)
        self.speed(speed)

    def flower(self, orig_angle1, orig_angle2):
        self._origin = self.position()
        for x in range(1, 21):
            self.triangle(orig_angle1, orig_angle2)

    def make_stem(self):
        pensize = self.pensize()
        self.pencolor('#238c13')
        self.pensize(6)
        self.setheading(270)
        self._starts.append(mike.position())
        self.forward(460)
        self.penup()
        self.to_origin()
        self.pendown()
        # Return pensize to however it was before method was called
        self.pensize(pensize)

    def run_through_levels(self):
        length = self._len
        if self._level > 2:
            print('time to end')
            return True
        for start in self._starts:
            self._starts = self._starts[1:]
            if len(self._starts) < 3 and self._level == 2:
                length = 3
            self.penup()
            self.goto(start)
            self.pendown()
            for i in range(1, 2):
                mod = length * i ** 0.9
                mike.flower((0, mod), (18, 40))
                mike.flower((0, mod), (-18, 40))

            self.pencolor((random(), random(), random()))
            self.incrememnt_level()
            # self._len *= 0.2
            self._len = 10
            self.run_through_levels()


window = turtle.Screen()

mike = TurtleArtist()
mike.goto(0, 100)
mike.pensize(1.1)
mike.shape('turtle')
mike.speed(500)
mike.make_stem()
mike.pencolor('#FBE54E')
mike.run_through_levels()

window.exitonclick()
