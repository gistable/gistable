#!/usr/bin/env python

#
# Usage: python extract_scene.py -p [filename] [classname]
# eg:    python extract_scene.py -p examples.py DrawCircle
#

import math
import numpy as np

import helpers
from scene import Scene
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from topics import functions

from mobject.tex_mobject import TexMobject




# Draw basic shapes

class DrawCircle(Scene):
    def construct(self):
        circle = Circle(color=WHITE,radius=1)
        self.play(ShowCreation(circle))


class DrawLine(Scene):
    def construct(self):
        START = (0,0,0)
        END =   (4,0,0)
        line = Line(START,END);
        self.play(ShowCreation(line))


class DrawRectangle(Scene):
    def construct(self):
        rect = Rectangle(height=3,width=4)
        self.play(ShowCreation(rect))


class DrawPolygon(Scene):
    def construct(self):
        Hexagon =   [(0,0,0),   #P1
                    (1,1,0),    #P2
                    (2,1,0),    #P3
                    (3,0,0),    #P4
                    (2,-1,0),   #P5
                    (1,-1,0)    #P6
                    ]

        poly = Polygon(*Hexagon)
        self.play(ShowCreation(poly))


class DrawVector(Scene):
    def construct(self):
        vector = Vector(direction=UP)
        self.play(ShowCreation(vector))


class DrawArc(Scene):
    def construct(self):
        angle = math.radians(180)
        arc =  Arc(radius=2,angle=angle)
        self.play(ShowCreation(arc))



# Move shapes
class MoveCircle(Scene):
    def construct(self):
        circle = Circle(radius=1,color=RED)
        end_point = (3,0,0)
        animation = ApplyMethod(circle.shift, end_point)
        self.play(animation)

class MoveVector(Scene):
    def construct(self):
        vector = Vector(direction=RIGHT)
        end_point = (4,0,0)
        animation = ApplyMethod(vector.shift,end_point)
        self.play(animation)


# Animate shapes

class RotateRect(Scene):
    def construct(self):
        rect  = Rectangle(height=1,width=2)
        angle = math.radians(90)
        animation = Rotate(rect, angle=angle)
        self.play(animation)


class ScaleCircle(Scene):
    def construct(self):
        circle = Circle(radius=2, fill_color=YELLOW, fill_opacity=1)
        self.play(GrowFromCenter(circle))


class RotatePolygon(Scene):
    def construct(self):
        Hexagon =   [(0,0,0),   #P1
                    (1,1,0),    #P2
                    (2,1,0),    #P3
                    (3,0,0),    #P4
                    (2,-1,0),   #P5
                    (1,-1,0)    #P6
                    ]

        poly = Polygon(*Hexagon)
        animation = Rotate(poly, angle=math.radians(180), in_place=True)
        self.play(animation)


class RotateSquareForever(Scene):
    def construct(self):
        square = Square()
        rotate = Rotating(square)
        self.play(rotate)


# Transform one shape to another

class LineToCircle(Scene):
    def construct(self):
        line = Line((0,0,0), (4,0,0))
        arc = Circle(color = WHITE, radius=1)
        self.play(ShowCreation(arc))
        self.play(Transform(arc, line))
        self.dither()

class DotToLine(Scene):
    def construct(self):
        dot = Dot()
        line = Line((0,0,0), (3,0,0))
        self.play(ShowCreation(dot))
        self.play(Transform(dot, line))
        self.dither()

class DotToCircle(Scene):
    def construct(self):
        circle = Circle()
        dot = Dot()
        self.play(ShowCreation(dot))
        self.play(Transform(dot, circle))
        self.dither()


class LineToSquare(Scene):
    def construct(self):
        line = Line((0,0,0),(3,0,0))
        square = Rectangle(width=3, height=3)
        # OR: square = Square()
        self.play(ShowCreation(line))
        self.play(Transform(line, square))
        self.dither()




# Functions and Equations

class PlotFunctionGraph(Scene):
    def construct(self):
        self.numpy_sin_function()
        self.clear()
        self.numpy_cos_function()
        self.clear()
        self.damped_sin_wave()
        self.clear()
        self.sigmoid_function()
        self.clear()
        self.soft_plus()

    def numpy_sin_function(self):
        function = np.sin
        wave = functions.FunctionGraph(function,x_min=-5,x_max=5)
        self.play(ShowCreation(wave))

    def numpy_cos_function(self):
        function = np.cos
        wave = functions.FunctionGraph(function,x_min=-5,x_max=5,color=RED)
        self.play(ShowCreation(wave))


    def damped_sin_wave(self):
        # y(t) = e^(-t)*cos(2*pi*t)
        function = lambda t: np.exp(-t)*np.cos(2*np.pi*t)
        wave = functions.FunctionGraph(function,x_min=-1,x_max=5)
        self.play(ShowCreation(wave))

    def sigmoid_function(self):

        function = helpers.sigmoid
        wave = functions.FunctionGraph(function,x_max=6,x_min=-6)
        self.play(ShowCreation(wave))

    def soft_plus(self):
        function = lambda t: np.log(1+np.exp(t))
        curve = functions.FunctionGraph(function,x_min=-6,x_max=7)
        self.play(ShowCreation(curve))



# combine and animate complex shapes
class DrawFlag(Scene):
    def construct(self):
        flag = Rectangle(height=1,width=1.9,stroke_width=1.5,fill_color=DARK_BLUE,fill_opacity=1)
        bottom_corner = flag.get_corner(LEFT+DOWN)
        pole = Line(bottom_corner,bottom_corner+(DOWN*2.5), stroke_width=1.5)
        flag.add(pole)
        self.play(ShowCreation(flag))
        self.dither()

class DrawStar(Scene):
    def construct(self):
        up_triangle = Polygon((0,0,0),(+2,-2,0),(-2,-2,0),stoke_width=1)
        down_triangle = Polygon(up_triangle.get_left()+LEFT*(0.5),
                                up_triangle.get_right()+RIGHT*(0.5),
                                up_triangle.get_bottom()+DOWN)
        self.play(ShowCreation(up_triangle))
        self.play(ShowCreation(down_triangle))


class MoveAlongPathAnimation(Scene):
    def construct(self):
        wave = functions.FunctionGraph(np.sin,x_min=-5,x_max=4)
        dot  = Dot(wave.points[0],color=RED,radius=0.2)
        self.play(ShowCreation(wave))
        self.play(GrowFromCenter(dot))
        self.play(MoveAlongPath(dot,wave),rate_time=5)


class DrawAndGate(Scene):
    def construct(self):

        AND_GATE = VGroup()

        arc = Arc(start_angle=3*np.pi/2,angle=np.pi,radius=0.6)
        body = Mobject(Line(arc.points[-1], arc.get_top()+LEFT),
                        Line(arc.get_top()+LEFT, arc.get_top()+LEFT+DOWN*1.2),
                        Line(arc.get_top()+LEFT+DOWN*1.2, arc.points[0]),
                        )


        arc_center = len(arc.points)/2 
        out =   Line(arc.points[arc_center],arc.points[arc_center]+RIGHT)

        input_a = Line(body[1].get_center()+UP*0.3,body[1].get_center()+UP*0.3+LEFT)
        input_b = Line(body[1].get_center()+DOWN*0.3,body[1].get_center()+DOWN*0.3+LEFT)

        AND_GATE.add(arc,body)
        self.play(ShowCreation(AND_GATE))

        self.play(ShowCreation(input_a),ShowCreation(input_b),ShowCreation(out))


class DivideCircleIntoParts(Scene):
    def construct(self):
        PARTS = 8
        ANGLE = 360/PARTS
        start_point = (-2,0,0)
        end_point = (2,0,0)
        
        circle = Circle(radius=2,color=WHITE)
        start_line = Line(start_point,end_point)
        copy = start_line.copy()

        center = Dot()

        self.play(ShowCreation(circle))
        self.play(ShowCreation(center))
        self.play(Transform(center,start_line))

        for i in range(PARTS/2):
            divider = copy.rotate(angle=math.radians(ANGLE), about_point=copy.get_center())
            to = Transform(start_line ,divider)
            self.play(to)
            self.add(divider.copy())
            self.dither()


class LightSourcePhoton(Scene):
    def construct(self):

        Amplitude = 0.4
        freq = 3
        angular_freq = (2*np.pi)*freq
        equation = lambda t: Amplitude*np.sin(t*angular_freq)

        photon = functions.FunctionGraph(equation,x_min=-5,x_max=-4)
        light_source = Dot(photon.points[0], radius=0.5, color=YELLOW)

        tip = Arrow(photon.points[-1],photon.points[-1]+RIGHT*0.4)
        self.play(GrowFromCenter(light_source))
        self.play(ShowCreation(photon))
        self.play(ShowCreation(tip))
        photon.add(tip)

        animation = ApplyMethod(photon.shift, (6,0,0))
        self.play(animation)


class Hydrogen(Scene):

    def construct(self):
        hydrogen_atom = Mobject()
        title = TexMobject("Hydrogen Atom")
        point_A = (-2,2,0)
        point_B = (-2,-2,0)
        arrow = Arrow(ORIGIN+LEFT*0.9,ORIGIN+RIGHT*0.9)
        add_sign  = TexMobject("+", stroke_width=0.7)

        orbit = Circle(radius=1.3).scale(0.85)
        proton = Dot(radius=0.4, color="GREY").scale(0.85)
        elec = Dot(radius=0.2, color="RED").scale(0.85)
        p_charge = TexMobject("+", stroke_width=0.5)
        e_charge = TexMobject("-",stroke_width=0.5)


        title.move_to(title.get_center()+UP*2)
        elec.move_to(orbit.points[0])
        e_charge.move_to(elec.get_center())
        p_charge.move_to(proton.get_center())

        self.play(ShowCreation(title))
        self.play(ShowCreation(orbit))
        self.play(GrowFromCenter(proton), GrowFromCenter(p_charge))
        self.play(GrowFromCenter(elec), GrowFromCenter(e_charge))

        self.play(MoveAlongPath(elec, orbit),MaintainPositionRelativeTo(e_charge, elec), run_time=5,rate_func=None)

        hydrogen_atom.add(orbit,elec, proton, e_charge, p_charge)
        atom_copy = hydrogen_atom.copy()

        h1_text = TexMobject("H").move_to(point_A+LEFT*2)
        h2_text = TexMobject("H").move_to(point_B+LEFT*2)


        names = VGroup(h1_text, h2_text)
        self.play(ApplyMethod(atom_copy.shift, point_A),ApplyMethod(hydrogen_atom.shift, point_B),Transform(title, names))


        add_sign.move_to(atom_copy.get_center()+DOWN*2)
        self.play(ShowCreation(add_sign),ShowCreation(arrow))

        h1_atom = atom_copy.copy().move_to(arrow.get_end()+RIGHT*3.5)
        h2_atom = hydrogen_atom.copy().move_to(arrow.get_end()+RIGHT*1.5)
        self.remove(atom_copy, hydrogen_atom)

        h2_atom[1].move_to(h2_atom[0].points[2])
        h2_atom[3].move_to(h2_atom[1].get_center())
        h1_atom[1].move_to(h1_atom[0].points[14])
        h1_atom[3].move_to(h1_atom[1].get_center())

        h2_molecule = VGroup(h1_atom,h2_atom)
        two_atoms = VGroup(atom_copy,hydrogen_atom) #org.copy()

        molecule_name = TexMobject("H_{2}").move_to(h2_molecule.get_center()+DOWN*2.5)
        self.play(Transform(two_atoms, h2_molecule), FadeOut(arrow.add(add_sign)))
        self.add(h2_molecule)
        self.remove(title,two_atoms)
        self.play(Transform(names, molecule_name))