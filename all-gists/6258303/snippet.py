#!/usr/bin/python

from PIL import Image, ImageColor
import math
import sys

def closest_color(incolor, colors):
    distances = []
    min_distance = 10000
    for color in colors:
        distance = math.sqrt((color[0]-incolor[0])**2+(color[1]-incolor[1])**2+(color[2]-incolor[2])**2)        

        if(distance < min_distance):
            min_distance = distance
            c = color

        if distance == 0:
            return c

    return c
            
def read_colors(filename):
    color_hash = {}
    i = Image.open(filename)
    img = i.convert('RGB')
    (width, height) = img.size
    for x in range(width):
        for y in range(height):
            # print img.getpixel( (x,y) )
            color_hash[img.getpixel( (x,y) )] = True
    return color_hash.keys()

def generate_clut(colors, outfile):
    im = Image.new("RGBA", (512, 512))
    for by in range(8):
        for bx in range(8):
            for g in range(64):
                for r in range(64):
                    x = r + bx*64
                    y = g + by*64

                    rc = min(255, int(r * 255.0 / 63.0 + 0.5))
                    gc = min(255, int(g * 255.0 / 63.0 + 0.5))
                    bc = min(255, int((bx + by * 8.0) * 255.0 / 63.0 + 0.5))
                    im.putpixel( (x,y), closest_color((rc,gc,bc), colors) )
    im.save(outfile)


if len(sys.argv)<3:
    print "usage: generate_clut input_image clut.png"
    sys.exit();

input_image = sys.argv[1]
output_image = sys.argv[2]

print "reading colors from %s" % input_image
colors = read_colors(input_image)
print "number of colors: %i" % len(colors)
print "generating color lookup table"
generate_clut(colors, output_image)
print "saved to %s" % output_image
