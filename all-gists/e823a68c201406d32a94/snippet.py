# -*- coding: utf-8 -*-
import bohrium as np
from math import pi
import matplotlib.pyplot as plt
import matplotlib.colors as colors

fig = plt.figure()
plt.xticks([])
plt.yticks([])

k       = 5    # number of plane waves
stripes = 37   # number of stripes per wave
N       = 512  # image size in pixels
ite     = 30   # iterations
phases  = np.arange(0, 2*pi, 2*pi/ite)

image = np.empty((N, N))

d = np.arange(-N/2, N/2, dtype=np.float64)

xv, yv = np.meshgrid(d, d)
theta  = np.arctan2(yv, xv)
r      = np.log(np.sqrt(xv*xv + yv*yv))
r[np.isinf(r) == True] = 0

tcos   = theta * np.cos(np.arange(0, pi, pi/k))[:, np.newaxis, np.newaxis]
rsin   = r * np.sin(np.arange(0, pi, pi/k))[:, np.newaxis, np.newaxis]
inner  = (tcos - rsin) * stripes

cinner = np.cos(inner)
sinner = np.sin(inner)

i = 0
for phase in phases:
    image[:] = np.sum(cinner * np.cos(phase) - sinner * np.sin(phase), axis=0) + k
    plt.imshow(image.copy2numpy(), cmap="RdGy")
    fig.savefig("quasi-{:03d}.png".format(i), bbox_inches='tight', pad_inches=0)
    i += 1
