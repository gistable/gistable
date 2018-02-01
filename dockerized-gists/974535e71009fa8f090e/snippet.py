#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np

from math import cos, sin, pi, sqrt, atan2
d2r = pi/180

class Geometry(object):
    def circle_intersection(self, circle1, circle2):
        '''
        @summary: calculates intersection points of two circles
        @param circle1: tuple(x,y,radius)
        @param circle2: tuple(x,y,radius)
        @result: tuple of intersection points (which are (x,y) tuple)
        '''
        # return self.circle_intersection_sympy(circle1,circle2)
        x1,y1,r1 = circle1
        x2,y2,r2 = circle2
        # http://stackoverflow.com/a/3349134/798588
        dx,dy = x2-x1,y2-y1
        d = sqrt(dx*dx+dy*dy)
        if d > r1+r2:
            print "#1"
            return None # no solutions, the circles are separate
        if d < abs(r1-r2):
            print "#2"
            return None # no solutions because one circle is contained within the other
        if d == 0 and r1 == r2:
            print "#3"
            return None # circles are coincident and there are an infinite number of solutions

        a = (r1*r1-r2*r2+d*d)/(2*d)
        h = sqrt(r1*r1-a*a)
        xm = x1 + a*dx/d
        ym = y1 + a*dy/d
        xs1 = xm + h*dy/d
        xs2 = xm - h*dy/d
        ys1 = ym - h*dx/d
        ys2 = ym + h*dx/d

        return (xs1,ys1),(xs2,ys2)

    def circle_intersection_sympy(self, circle1, circle2):
        from sympy.geometry import Circle, Point
        x1,y1,r1 = circle1
        x2,y2,r2 = circle2
        c1=Circle(Point(x1,y1),r1)
        c2=Circle(Point(x2,y2),r2)
        intersection = c1.intersection(c2)
        if len(intersection) == 1:
            intersection.append(intersection[0])
        p1 = intersection[0]
        p2 = intersection[1]
        xs1,ys1 = p1.x,p1.y
        xs2,ys2 = p2.x,p2.y
        return (xs1,ys1),(xs2,ys2)

def test_circle_intersection():
    geom = Geometry()
    np.testing.assert_almost_equal(
        geom.circle_intersection((0,0,1),(2,0,1)),
        ((1,0),(1,0)))
    np.testing.assert_almost_equal(
        geom.circle_intersection((2,0,1),(0,0,1)),
        ((1,0),(1,0)))
    np.testing.assert_almost_equal(
        geom.circle_intersection((1,1,1),(3,1,1)),
        ((2,1),(2,1)))
    np.testing.assert_almost_equal(
        geom.circle_intersection((0,0,1),(cos(d2r*45)*2,0,1)),
        ((cos(d2r*45),-sin(d2r*45)),
         (cos(d2r*45),+sin(d2r*45))))
