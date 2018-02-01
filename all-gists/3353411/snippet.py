from numpy.random import rand
from numpy import r_, ix_, uint8, roll
import matplotlib.pyplot as plt
import time

size = 200
GRID = (rand(size,size) > 0.75).astype(uint8)
# Rotate indices because the world is round
indx = r_[0:size]
up = roll(indx, -1)
down = roll(indx, 1)

fig = plt.figure()
ax = fig.add_subplot(111)
img = ax.imshow(GRID,interpolation='nearest',cmap='gray')

def update_image(idleevent):
    if update_image.i==2000:
        return False

    global GRID
    neighbors = GRID[up,:] + GRID[down,:] + GRID[:,up] + GRID[:,down] + \
        GRID[ix_(up,up)] + GRID[ix_(up,down)] + GRID[ix_(down,up)] + \
        GRID[ix_(down,down)]
    GRID = (neighbors == 3) | (GRID & (neighbors==2))

    img.set_data(GRID)
    fig.canvas.draw_idle()
    time.sleep(0.02)
    update_image.i += 1

update_image.i = 0

import wx
wx.EVT_IDLE(wx.GetApp(), update_image)
plt.show()
