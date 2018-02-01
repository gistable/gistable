# Python port of Paul Bourke's http://local.wasp.uwa.edu.au/~pbourke/fractals/lyapunov/gen.c
# By Johan Bichel Lindegaard - http://johan.cc

import math
import random
from PIL import Image, ImageDraw
import argparse
import os

parser = argparse.ArgumentParser(description='Search for chaos.')
#parser.add_argument('-i', dest='maxiterations' metavar='N', type=int,
#            help='Maximum iterations.')

args = parser.parse_args()

MAXITERATIONS = 100000
NEXAMPLES = 1000

def createAttractor():
    for n in range(NEXAMPLES):        
        lyapunov = 0
        xmin= 1e32
        xmax=-1e32
        ymin= 1e32
        ymax=-1e32
        ax, ay, x, y = [], [], [], []
        
        # Initialize coefficients for this attractor
        for i in range(6):
            ax.append(random.uniform(-2, 2))
            ay.append(random.uniform(-2, 2))
    
        # Calculate the attractor
        drawit = True;
        x.append(random.uniform(-0.5, 0.5))
        y.append(random.uniform(-0.5, 0.5))
        
        d0 = -1
        while d0 <= 0:
            xe = x[0] + random.uniform(-0.5, 0.5) / 1000.0
            ye = y[0] + random.uniform(-0.5, 0.5) / 1000.0
            dx = x[0] - xe
            dy = y[0] - ye
            d0 = math.sqrt(dx * dx + dy * dy)

        for i in range(MAXITERATIONS):
            # Calculate next term
            
            x.append(ax[0] + ax[1]*x[i-1] + ax[2]*x[i-1]*x[i-1] + ax[3]*x[i-1]*y[i-1] + ax[4]*y[i-1] + ax[5]*y[i-1]*y[i-1])
            y.append(ay[0] + ay[1]*x[i-1] + ay[2]*x[i-1]*x[i-1] + ay[3]*x[i-1]*y[i-1] + ay[4]*y[i-1] + ay[5]*y[i-1]*y[i-1])
            xenew = ax[0] + ax[1]*xe + ax[2]*xe*xe + ax[3]*xe*ye + ax[4]*ye + ax[5]*ye*ye
            yenew = ay[0] + ay[1]*xe + ay[2]*xe*xe + ay[3]*xe*ye + ay[4]*ye + ay[5]*ye*ye

            # Update the bounds 
            xmin = min(xmin,x[i])
            ymin = min(ymin,y[i])
            xmax = max(xmax,x[i])
            ymax = max(ymax,y[i])

            # Does the series tend to infinity
            if xmin < -1e10 or ymin < -1e10 or xmax > 1e10 or ymax > 1e10:
                drawit = False
                print "infinite attractor"
                break

            # Does the series tend to a point
            dx = x[i] - x[i-1]
            dy = y[i] - y[i-1]
            if abs(dx) < 1e-10 and abs(dy) < 1e-10:
                drawit = False
                print "point attractor"
                break
            

            # Calculate the lyapunov exponents
            if i > 1000:
                dx = x[i] - xenew
                dy = y[i] - yenew
                dd = math.sqrt(dx * dx + dy * dy)
                lyapunov += math.log(math.fabs(dd / d0))
                xe = x[i] + d0 * dx / dd
                ye = y[i] + d0 * dy / dd
            
        # Classify the series according to lyapunov
        if drawit:
            if abs(lyapunov) < 10:
                print "neutrally stable"
                drawit = False
            elif lyapunov < 0:
                print "periodic {} ".format(lyapunov)
                drawit = False 
            else:
                print "chaotic {} ".format(lyapunov) 
            
        # Save the image
        if drawit:
            saveAttractor(n,ax,ay,xmin,xmax,ymin,ymax,x,y)

def saveAttractor(n,a,b,xmin,xmax,ymin,ymax,x,y):
    width, height = 500, 500
    
    if not os.path.exists("output"):
        os.makedirs("output")

    # Save the parameters
    with open("output/{}.txt".format(n), "w") as f:
        f.write("{} {} {} {}\n".format(xmin, ymin, xmax, ymax))
        for i in range(6):
            f.write("{} {}\n".format(a[i], b[i]))
        f.close()
    
    # Save the image
    image = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(image)
    
    for i in range(MAXITERATIONS):
        ix = width * (x[i] - xmin) / (xmax - xmin)
        iy = height * (y[i] - ymin) / (ymax - ymin)
        if i > 100:
            draw.point([ix, iy], fill="black")
    
    image.save("output/{}.png".format(n), "PNG")
    print "saved attractor to ./output/{}.png".format(n)

createAttractor()