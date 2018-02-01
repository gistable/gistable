# Tests for antialiasing a high-frequency image in various ways
# Nathan Reed, July 2014
# Written for Python 3.4; requires numpy and Pillow to be installed

import concurrent.futures
import math
import multiprocessing
import numpy as np
import optparse
import random
import sys
import threading
from PIL import Image

# Parse command-line options
parser = optparse.OptionParser()
parser.add_option('-o', '--output', dest='outputPath', default='aa.bmp', help='Write output to FILE', metavar='FILE')
parser.add_option('-d', '--dims', dest='dims', default='512x512', help='Image width x height, e.g. 640x480')
parser.add_option('-s', '--samples', dest='samples', default=16, help='Number of samples per pixel')
parser.add_option('-k', '--kernel', dest='kernel', default='gaussian', help='Antialiasing kernel to use. Choices are: box, gaussian, lanczos')
parser.add_option('-r', '--radius', dest='radius', default=1.0, help='Kernel radius in pixels')
parser.add_option('--splat', dest='splat', default=False, action='store_true', help='Enable splatting mode (otherwise, per-pixel mode)')
options, _ = parser.parse_args()

dX, dY = (int(n) for n in options.dims.lower().split('x'))
options.samples = int(options.samples)
options.kernel = options.kernel.lower()
options.radius = float(options.radius)
radiusX = options.radius / dX
radiusY = options.radius / dY

# Some kernels can't be sampled directly and require weights (which slow things down).
# In splatting mode, we always use weights.
needWeights = (options.kernel in ('lanczos',)) or options.splat

# Here's the image function we'll use to test antialiasing; it has infinite-frequency edges,
# plus the placement of the edges varies in spatial frequency over the image
minPeriod = 2e-5
maxPeriod = 0.2
def evalImage(x, y):
	period = minPeriod + (maxPeriod - minPeriod) * y**2
	phase = x / period
	phase -= np.floor(phase)
	return phase.round()

# Pixel center positions, to which offsets will be added to get sample positions
# (1D arrays, but shaped for broadcasting correctly with 2D arrays)
centerX = np.linspace(0.5/dX, 1.0 - 0.5/dX, dX).reshape((1, dX))
centerY = np.linspace(0.5/dY, 1.0 - 0.5/dY, dY).reshape((dY, 1))

# Create an array into which results will be accumulated
img = np.zeros((dY, dX))
if needWeights:
	totalWeight = np.zeros((dY, dX))
samplesDone = 0
imgLock = threading.Lock()

def accumulateImage(imgLocal, weight):
	# Accumulate into the global image
	with imgLock:
		global img
		img += imgLocal
		if needWeights:
			global totalWeight
			totalWeight += weight

		# Report progress now and then
		global samplesDone
		samplesDone += 1
		if (samplesDone + 1) % 128 == 0:
			print("Completed %d samples/px" % (samplesDone + 1))

def evalSample(_):
	weight = None

	# Generate samples according to the desired kernel
	if options.kernel == 'box':
		sampleX = centerX + np.random.uniform(-radiusX, radiusX, size=(dY, dX))
		sampleY = centerY + np.random.uniform(-radiusY, radiusY, size=(dY, dX))

	elif options.kernel == 'gaussian':
		# For gaussian samples, treat "radius" as the 3-sigma radius
		sampleX = centerX + np.random.normal(scale = radiusX / 3.0, size=(dY, dX))
		sampleY = centerY + np.random.normal(scale = radiusY / 3.0, size=(dY, dX))

	elif options.kernel == 'lanczos':
		# Can't directly sample Lanczos kernel, so just box-sample and weight appropriately
		sampleX = np.random.uniform(-options.radius, options.radius, size=(dY, dX))
		sampleY = np.random.uniform(-options.radius, options.radius, size=(dY, dX))
		weight = (np.sin(np.pi * sampleX) * np.sin(np.pi * sampleY) *
				  np.sin(np.pi * sampleX / options.radius) * np.sin(np.pi * sampleY / options.radius) /
				  (sampleX**2 * sampleY**2))
		sampleX = centerX + sampleX / dX
		sampleY = centerY + sampleY / dY

	else:
		sys.exit("Unknown kernel type '%s'" % options.kernel)

	# Evaluate the image at the generated sample positions
	img = evalImage(sampleX, sampleY)
	if needWeights:
		img *= weight

	accumulateImage(img, weight)

def evalSampleSplat(_):
	# Generate stratified samples over the image plane, jittering within each pixel square
	sampleJitterX = np.random.uniform(-0.5, 0.5, size=(dY, dX))
	sampleJitterY = np.random.uniform(-0.5, 0.5, size=(dY, dX))
	sampleX = centerX + sampleJitterX/dX
	sampleY = centerY + sampleJitterY/dY

	# Evaluate the image at the generated sample positions
	imgSamples = evalImage(sampleX, sampleY)

	# Splat each sample result onto nearby pixels according to the desired kernel
	img = np.zeros((dY, dX))
	totalWeight = np.zeros((dY, dX))
	radiusCeil = int(math.ceil(options.radius))
	for offsetY in range(-radiusCeil, radiusCeil+1):
		# Calculate vectors from each sample to the pixel centers at the current offset
		sampleOffsetY = sampleJitterY - offsetY
		for offsetX in range(-radiusCeil, radiusCeil+1):
			sampleOffsetX = sampleJitterX - offsetX

			if options.kernel == 'box':
				weight = (np.where(np.abs(sampleOffsetX) <= options.radius, 1.0, 0.0) *
						  np.where(np.abs(sampleOffsetY) <= options.radius, 1.0, 0.0))

			elif options.kernel == 'gaussian':
				# For gaussian samples, treat "radius" as the 3-sigma radius
				weight = np.exp(-0.5 * (sampleOffsetX**2 + sampleOffsetY**2) / ((options.radius / 3.0)**2))

			elif options.kernel == 'lanczos':
				weight = (np.sin(np.pi * sampleOffsetX) * np.sin(np.pi * sampleOffsetY) *
						  np.sin(np.pi * sampleOffsetX / options.radius) * np.sin(np.pi * sampleOffsetY / options.radius) /
						  (sampleOffsetX**2 * sampleOffsetY**2))

			else:
				sys.exit("Unknown kernel type '%s'" % options.kernel)

			weightedSamples = weight * imgSamples
			img[max(0, offsetY) : dY + min(0, offsetY), max(0, offsetX) : dX + min(0, offsetX)] += (
				weightedSamples[max(0, -offsetY) : dY + min(0, -offsetY), max(0, -offsetX) : dX + min(0, -offsetX)])
			totalWeight[max(0, offsetY) : dY + min(0, offsetY), max(0, offsetX) : dX + min(0, offsetX)] += (
				weight[max(0, -offsetY) : dY + min(0, -offsetY), max(0, -offsetX) : dX + min(0, -offsetX)])

	accumulateImage(img, totalWeight)

# Accumulate samples into an image, using a pool of worker threads
with concurrent.futures.ThreadPoolExecutor(max_workers = multiprocessing.cpu_count()) as pool:
	pool.map(evalSampleSplat if options.splat else evalSample, range(options.samples))

if needWeights:
	img /= totalWeight
else:
	img /= options.samples

# Convert to sRGB
img = img.clip(0.0, 1.0)
img = np.where(img <= 0.0031308, 12.92*img, 1.055*img**(1.0/2.4) - 0.055)

# Convert to 8-bit, send to PIL and save
img8Bit = np.uint8(np.rint(img * 255.0))
Image.fromarray(img8Bit).save(options.outputPath)
print('Wrote output to %s' % options.outputPath)
