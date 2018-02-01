#!/usr/local/bin/python3

import glob
import h5py
import matplotlib.animation as animation
import matplotlib.pyplot as plot
import numpy as np
import tensorflow as tf


def main():
    datafiles = glob.glob('data/*.h5')
    for datafile in datafiles:
        with h5py.File(datafile) as data:
            figure = plot.figure()
            imageplot = plot.imshow(np.zeros((227, 227, 3), dtype=np.uint8))

            def next_frame(i):
                image = 255 - data['images'][i].transpose(1, 2, 0)[:, :, ::-1]
                imageplot.set_array(image)
                return imageplot,

            animate = animation.FuncAnimation(figure, next_frame, frames=range(len(data['images'])), interval=252, blit=False)
            plot.show()



if __name__ == '__main__':
    main()
