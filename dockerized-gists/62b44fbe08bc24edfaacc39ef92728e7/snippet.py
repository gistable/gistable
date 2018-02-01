from __future__ import division, print_function, absolute_import

import numpy as np
import matplotlib.pyplot as plt

MAXITERS = 100


def mandelbrot_boettcher(z):
    zn = z
    B = z
    maxabszn = 0.0

    for n in range(1, MAXITERS + 1):
        B *= (1 + z/zn**2)**(1/2**n)
        zn = zn**2 + z
        abszn = np.abs(zn)
        if abszn > maxabszn:
            maxabszn = abszn
        if abszn > 1e100:
            return B

    if maxabszn > 2:
        return B
    else:
        return np.nan

mandelbrot_boettcher = np.vectorize(mandelbrot_boettcher, otypes=(np.complex128,))


def main():
    # Simple comparison to Mathematica page
    print("B(1.0) = {}".format(mandelbrot_boettcher(1.0)))
    print("B(1/3) = {}".format(mandelbrot_boettcher(1/3)))
    print("B(1 + 1j) = {}".format(mandelbrot_boettcher(1 + 1j)))
    print("B(0.1) = {}".format(mandelbrot_boettcher(0.1)))

    # Plot it
    x, y = np.linspace(-2.6, 1, 200), np.linspace(-1, 1, 200)
    x, y = np.meshgrid(x, y)
    z = x + 1j*y

    B = mandelbrot_boettcher(z)
    B = np.nan_to_num(B)
    plt.pcolormesh(x, y, abs(B))
    plt.show()


if __name__ == '__main__':
    main()
