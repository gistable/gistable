# Assumes you have a np.array((height,width,3), dtype=float) as your HDR image

import numpy as np

f = open("xxx.hdr", "wb")
f.write("#?RADIANCE\n# Made with Python & Numpy\nFORMAT=32-bit_rle_rgbe\n\n")
f.write("-Y {0} +X {1}\n".format(image.shape[0], image.shape[1]))

brightest = np.maximum(np.maximum(image[...,0], image[...,1]), image[...,2])
mantissa = np.zeros_like(brightest)
exponent = np.zeros_like(brightest)
np.frexp(brightest, mantissa, exponent)
scaled_mantissa = mantissa * 256.0 / brightest
rgbe = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
rgbe[...,0:3] = np.around(image[...,0:3] * scaled_mantissa[...,None])
rgbe[...,3] = np.around(exponent + 128)

rgbe.flatten().tofile(f)
f.close()