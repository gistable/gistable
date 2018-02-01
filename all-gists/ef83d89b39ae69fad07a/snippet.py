#!/usr/bin/env python3
import numpy as np
from math import sin, cos, pi, sqrt
import svgwrite
import itertools

def cam(f):
	""" Returns a camera matrix for the given focal length """
	return np.array(((1,0,0,0),
					 (0,1,0,0),
					 (0,0,1/f,0),
					 (0,0,0,1)))

def trans(δ):
	""" Returns a translation matrix for the given offset """
	x,y,z = δ
	return np.array(((1,0,0,x),
					 (0,1,0,y),
					 (0,0,1,z),
					 (0,0,0,1)))

def rotx(θ):
	""" Returns a rotation matrix for the given angle about the X axis """
	return np.array(((1,0,0,0),
					 (0,cos(θ),-sin(θ),0),
					 (0,sin(θ),cos(θ),0),
					 (0,0,0,1)))

def roty(θ):
	""" Returns a rotation matrix for the given angle about the X axis """
	return np.array(((cos(θ),0,sin(θ),0),
					 (0,1,0,0),
					 (-sin(θ),0,cos(θ),0),
					 (0,0,0,1)))

def rotz(θ):
	""" Returns a rotation matrix for the given angle about the X axis """
	return np.array(((cos(θ), -sin(θ),0,0),
					 (sin(θ), cos(θ),0,0),
					 (0,0,1,0),
					 (0,0,0,1)))

def rot(α, β, γ):
	return np.dot(np.dot(rotx(γ), roty(β)), rotz(α))

def rotate(α, β, γ, xs):
	rm = rot(α, β, γ)
	return [ np.dot(rm, hom(p))[:3].flatten() for p in xs ]

def proj(pos, angle, f):
	""" Returns a projection matrix for the given camera coordinates, angle and focal length """
#	print('TRN:\n', trans(-np.array(pos)))
#	print('ROT:\n', rot(*angle))
#	print('CAM:\n', cam(f))
	return np.dot(np.dot(cam(f), rot(*angle)), trans(-np.array(pos)))

def hom(vec):
	""" Returns a homogenous representation of vec """
	x,y,z = vec
	return np.transpose(np.array(((x,y,z,1),)))

def circ(r, θ):
	""" Returns a point on a 2D-circle """
	return cos(θ)*r, sin(θ)*r

def tetraeder(a):
	""" Returns the corners of a tetraeder with edge length a and its base surface in the xy-plane centered on the
	coordinate origin. """
	h = sqrt(2/3)*a
	r = sqrt(3)/3*a
	x1, y1 = circ(r, -pi/6)
	x2, y2 = circ(r, -5*pi/6)
	return ( (x1, y1, 0), (x2, y2, 0), (0, r, 0), (0, 0, h) )

dwg = svgwrite.Drawing('tetraeder.svg', profile='tiny')
l = 0.3
STEPS = 40
STEPX = 40
# Let's just call these units of length “meters”.
for offx in range(STEPS):
	pm = proj((0,0.2,-1), (0,0,1.47), 0.035)
#	print(pm)

	g = dwg.g(id='tetraeder-'+str(offx))

	project = lambda xs: [ np.dot(pm, hom(x))[:2].flatten() for x in xs ]

	cv = lambda ps: [ (x*100 + offx*STEPX, y*100) for x,y in ps ]

	def makeedge(dwg, g, *xs):
		ps = cv(project(xs))
		g.add(dwg.line(*ps, stroke=svgwrite.rgb(0,0,0,'%'), fill='none'))

	tet = rotate(offx/STEPS*2*pi, 0, 0, tetraeder(l))
	for p, q in itertools.permutations(tet, 2):
		makeedge(dwg, g, p, q)

	dwg.add(g)
	dwg.add(dwg.text(str(offx), insert=(offx*STEPX, -80), fill='black'))
dwg.save()
