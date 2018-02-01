# This borrows heavily from:
#   http://jsfiddle.net/Rebug/5uLr7s6o/
#
# Resulting gif:
#   http://dailydrawbot.tumblr.com/post/134989689114/an-archimedean-spherical-spiral

import math
import colorsys

def circle(pt, radius):
    x, y = pt
    diameter = radius * 2
    oval(x - radius, y - radius, diameter, diameter)

def rotatePointsX(points, angle):
    for x, y, z in points:
        y1 = y*cos(angle) - z*sin(angle)
        z1 = y*sin(angle) + z*cos(angle)
        x1 = x
        yield x1, y1, z1

def rotatePointsY(points, angle):
    for x, y, z in points:
        z1 = z*cos(angle) - x*sin(angle)
        x1 = z*sin(angle) + x*cos(angle)
        y1 = y
        yield x1, y1, z1

def rotatePointsZ(points, angle):
    for x, y, z in points:
        x1 = x*cos(angle) - y*sin(angle)
        y1 = x*sin(angle) + y*cos(angle)
        z1 = z
        yield x1, y1, z1

#  Create spherical spiral for given turns with almost same gap distance
#  @see [Archimedean Spherical Spiral]{@link http://en.wikipedia.org/wiki/Spiral#Spherical_spiral}
#  @param {number} turns - Times of turns around z-axis
#  @param {number} [count=800] - Number of points on spiral
#  @param {number} [radius=1] - Radius of sphere
#  @returns {Point[]} - Points (r,θ,φ) of spiral in spherical coordinates
def createSphericalSpiral(turns, count=800, radius=1, startPhase=0):
    # Spherical coordinate system in mathematics
    # (radial distance r, azimuthal angle θ, polar angle φ)
    # @see [Spherical coordinate system]{@link http://en.wikipedia.org/wiki/Spherical_coordinate_system}
    step = 2 / count
    i = -1
    # for(var i = -1; i <= 1; i += step) {
    while i <= 1.0:
        phi = math.acos(i);
        theta = (2 * turns * phi + startPhase) % (2 * math.pi)
        yield (radius, phi, theta)
        i += step

#  Convert from spherical coordinates (r,θ,φ) to Cartesian coordinates (x,y,z)
#  @see {@link http://en.wikipedia.org/wiki/Spherical_coordinate_system#Cartesian_coordinates}
#  @param {{radius:number,theta:number,phi:number}} point - Point in spherical coordinates
#  @returns {{x:number,y:number,z:number}} - Point in Cartesian coordinates
def convert2xyz(points):
    for radius, phi, theta in points:
        phi += 0
        theta += 0
        x = radius * math.sin(phi) * math.sin(theta)
        y = radius * math.sin(phi) * math.cos(theta)
        z = radius * math.cos(phi)
        yield (x, y, z)

canvasHeight = 500
canvasWidth = canvasHeight
sphereRadius = 0.363 * canvasHeight
circleRadius = 0.04 * canvasHeight

grayRange = 0.9
maxTurns = 9
nCircles = 1000
nFrames = 100

for frame in range(nFrames):
    t = (frame/nFrames + 1/12) % 1.0
    newPage(canvasWidth, canvasHeight)
    frameDuration(1/12.5)
    fill(0.0)
    rect(0, 0, canvasWidth, canvasHeight)
    translate(canvasWidth/2, canvasHeight/2)

    points = convert2xyz(createSphericalSpiral(maxTurns * sin(t*2*pi), nCircles, 1.0, 0))

    points = rotatePointsX(points, -t*2*pi + 0.0 * pi)
    points = rotatePointsZ(points, -t*2*pi + 0.25 * pi)
    points = rotatePointsY(points, -t*2*pi + 0.0 * pi)

    for x, y, z in sorted(points, key=lambda pt: pt[1]):
        gray = (y + 1) * 0.5
        rgb = colorsys.hsv_to_rgb(0.15, 0.16, (1 - grayRange) + gray * grayRange)
        fill(*rgb)
        circle((x*sphereRadius, z*sphereRadius), circleRadius)

saveImage("SphericalSpiral.gif")
