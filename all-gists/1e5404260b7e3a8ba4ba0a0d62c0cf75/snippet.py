from __future__ import print_function

import sys
import random

from collections import deque

from PIL import Image

# THIS IS THE MAGIC VALUE THAT MAKES EVERYTHING GLITCHED
# DEFAULT: 0.00001 (good w/ 20 iterations)
# FUN VALUES: 0.001 w/ 3 iterations
glitchulate_factor = 0.00001

def glitchulate(width, input,rec=False):

    add = []

    if random.random() < glitchulate_factor:
        if random.random() > 0.5:
            input.rotate(width)
        else:
            input.rotate(-width)
    if len(input) < 10000:
        r2 = input

    else:
        place = int(random.random() * (len(input)-2))
        r2 = deque(list(input)[place:])
        add = deque(glitchulate(width, deque(list(input)[:place]), True))

    r = []

    skip = 0
    skipped = 0

    for x in r2:
        if skip:
            skipped += 1
            skip = skip - 1
            continue

        if random.random() < glitchulate_factor:
            r.append(int(random.random()*128))
            r.append(x)

        elif random.random() < glitchulate_factor:
            r.append(x)
            skip = 2

        elif random.random() < 0.01:
            k = int(x - random.random() * 5)
            if k >= 0:
                r.append(k)
            else:
                r.append(0)

        elif random.random() < 0.01:
            k = int(x + random.random() * 5)
            if k < 255:
                r.append(k)
            else:
                r.append(254)

        else:
            r.append(x)

    for skip in range(skipped):
        r.append(0)

    return deque(list(add) + list(r))

im = Image.open(sys.argv[2])
rgb = im.split()

rgbdata = [deque(), deque(), deque()]
pointdata = []

for layer, data in zip(rgb, rgbdata):
    pointdata = []

    for y in range(im.height):
        for x in range(im.width):
            pointdata.append((x, y))
            data.append(layer.getpixel((x, y)))


print('beginning glitchulation')
r, g, b = rgbdata

for frame in range(int(sys.argv[1])+1):

    if random.random() < glitchulate_factor*100:
        width = int(im.height/100 * im.width) * int(random.random() * 5)

        if random.random() > 0.5:
            r.rotate(width)
            g.rotate(width)
            b.rotate(width)
        else:
            r.rotate(-width)
            g.rotate(-width)
            b.rotate(-width)

    print("Frame", frame)

    if random.random() < glitchulate_factor * 10000:
        if random.random() > 0.5:
            glitchulate_factor = glitchulate_factor * 3
            if glitchulate_factor > 0.002:
                # Time to drop this...
                glitchulate_factor = 0.0001
                print("Too glitched! Now ", glitchulate_factor)
            else:
                print("Upping the glitchuation to", glitchulate_factor)
        else:
            glitchulate_factor = glitchulate_factor / 2
            print("Dropping the glitchulation to", glitchulate_factor)

    r = glitchulate(im.width, r)
    g = glitchulate(im.width, g)
    b = glitchulate(im.width, b)

    if frame == int(sys.argv[1]):
        print("Assembling...")
        im2 = Image.new(im.mode, im.size)

        for c, x in enumerate(pointdata):
            im2.putpixel(x, (r[c], g[c], b[c]))

        print("Saving to disk...")
        im2.save("glitch.jpg")
