"""From the numba examples
(https://github.com/numba/numba/blob/master/examples/mandel.py),
but tweaked to recalculate on the fly as the viewport changes"""
from numba import autojit
import numpy as np
from pylab import imshow, jet, show, ion
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['image.origin'] = 'lower'

@autojit
def mandel(x, y, max_iters):
    """
    Given the real and imaginary parts of a complex number,
    determine if it is a candidate for membership in the Mandelbrot
    set given a fixed number of iterations.
    """
    i = 0
    c = complex(x,y)
    z = 0.0j
    for i in range(max_iters):
        z = z*z + c
        if (z.real*z.real + z.imag*z.imag) >= 4:
            return i

    return 255

@autojit
def create_fractal(min_x, max_x, min_y, max_y, image, iters):
    height = image.shape[0]
    width = image.shape[1]

    pixel_size_x = (max_x - min_x) / width
    pixel_size_y = (max_y - min_y) / height
    for x in range(width):
        real = min_x + x * pixel_size_x
        for y in range(height):
            imag = min_y + y * pixel_size_y
            color = mandel(real, imag, iters)
            image[y, x] = color

    return image

def update_axes(ax):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    trans = ax.transAxes
    ext = trans.transform([[1, 1]]) - trans.transform([[0, 0]])
    nx = ext[0, 0]
    ny = ext[0, 1]
    image = np.zeros((ny, nx), dtype=np.uint8)
    create_fractal(xlim[0], xlim[1], ylim[0], ylim[1], image, 255)
    ax.clear()
    ax.imshow(image, extent=[xlim[0], xlim[1], ylim[0], ylim[1]], zorder=0)
    ax.figure.canvas.draw()

image = np.zeros((500, 750), dtype=np.uint8)
artist = plt.imshow(create_fractal(-2.0, 1.0, -1.0, 1.0, image, 255),
                    extent=[-2.0, 1.0, -1.0, 1.0])

ax = plt.gca()
ax.figure.canvas.mpl_connect('button_release_event', lambda x: update_axes(ax))
ax.set_title('Zoom in')
plt.show()
