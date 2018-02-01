# Simulator for depth comparison error (i.e. z-fighting)
# Nathan Reed, June 2015
# Written for Python 3.4; requires numpy

import math
import numpy as np
import optparse

# Parse command-line options
parser = optparse.OptionParser()
parser.add_option('-n', '--near', dest='near', default=0.1, help='Near plane distance')
parser.add_option('-f', '--far', dest='far', default=10000, help='Far plane distance')
parser.add_option('-t', '--tests', dest='num', default=10000, help='Number of depth values to test')
parser.add_option('--log', dest='log', default=False, action='store_true', help='Enable logarithmic distribution of test depths (default is linear)')
options, _ = parser.parse_args()

near = float(options.near)
far = float(options.far)
numVals = int(options.num)

np.random.seed(4177)	# Arbitrarily-chosen fixed seed, for reproducible pseudorandom values

# Map a sorted sequence of z-values through view/projection matrices, quantizing to float32 at each
# step and to the final depth format (float32 or int24) at the end, then count how many places a
# pair of adjacent z-values either changed order, or became indistinguishable due to mapping to the
# same value.

if options.log:
	zValsF64 = np.exp(np.linspace(math.log(near), math.log(far), numVals+1, dtype=np.float64))
else:
	zValsF64 = np.linspace(near, far, numVals+1, dtype=np.float64)
zVals = zValsF64.astype(np.float32)

def ReportErrorCount(name, dVals):
	numIndist = np.sum(dVals[1:] == dVals[:-1])
	numSwaps = np.sum(dVals[1:] < dVals[:-1])
	numProblems = numIndist + numSwaps
	print('%s: %d problems (%0.2f%%); %d indistinguishable + %d swaps' %
			(name, numProblems, 100.0 * numProblems/numVals, numIndist, numSwaps))

def GenerateHistograms(path, zVals, dVals):
	indist = zVals[np.argwhere(dVals[1:] == dVals[:-1])]
	swaps  = zVals[np.argwhere(dVals[1:] < dVals[:-1])]
	bins = 50
	histoIndist, binEdges = np.histogram(indist, bins, range=(near, far))
	histoSwaps,  _        = np.histogram(swaps, bins, range=(near, far))
	with open(path, 'wt') as outFile:
		outFile.write('Z\tIndist\tSwaps\n')
		for i in range(bins):
			outFile.write('%f\t%f\t%f\n' % (binEdges[i], histoIndist[i], histoSwaps[i]))

def QuantizeToInt24(dVals):
	lastValue = (1 << 24) - 1
	return np.rint(dVals * lastValue)

print('===== Projection only =====')

# Control test: the unaltered z-values
ReportErrorCount('Unaltered z values, float32', zVals)
ReportErrorCount('Unaltered z values, int24', QuantizeToInt24(zVals / far))

print()

# Standard projection matrix
zScale = far / (far - near)
zBias = -near * zScale
dVals = (zVals * zScale + zBias) / zVals
ReportErrorCount('Standard projection, float32', dVals)
ReportErrorCount('Standard projection, int24', QuantizeToInt24(dVals))
GenerateHistograms('histo_01_standard_float32.txt', zVals, dVals)

# Infinite projection matrix
zScale = 1.0
zBias = -near * zScale
dVals = (zVals * zScale + zBias) / zVals
ReportErrorCount('Infinite projection, float32', dVals)
ReportErrorCount('Infinite projection, int24', QuantizeToInt24(dVals))

# Reversed-Z projection matrix
zScale = near / (near - far)
zBias = -far * zScale
dVals = (zVals * zScale + zBias) / zVals
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('Reversed-Z, float32', dVals)
ReportErrorCount('Reversed-Z, int24', QuantizeToInt24(dVals))

# Reversed-Z infinite projection matrix
zScale = 0.0
zBias = near
dVals = (zVals * zScale + zBias) / zVals
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('Infinite reversed-Z, float32', dVals)
ReportErrorCount('Infinite reversed-Z, int24', QuantizeToInt24(dVals))

print()

# OpenGL-style, standard projection matrix
zScale = (far + near) / (far - near)
zBias = -2.0 * near * far / (far - near)
dVals = (zVals * zScale + zBias) / zVals
dVals = 0.5 * dVals + 0.5	# OpenGL viewport transform
ReportErrorCount('GL-style standard, float32', dVals)
ReportErrorCount('GL-style standard, int24', QuantizeToInt24(dVals))

# OpenGL-style, infinite projection matrix
zScale = 1.0
zBias = -2.0 * near
dVals = (zVals * zScale + zBias) / zVals
dVals = 0.5 * dVals + 0.5	# OpenGL viewport transform
ReportErrorCount('GL-style infinite, float32', dVals)
ReportErrorCount('GL-style infinite, int24', QuantizeToInt24(dVals))

# Reversed-Z has no effect on precision in the default OpenGL [-1, 1] depth range
'''
# OpenGL-style, reversed-Z projection matrix
zScale = (near + far) / (near - far)
zBias = -2.0 * far * near / (near - far)
dVals = (zVals * zScale + zBias) / zVals
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('GL-style reversed-Z, float32', dVals)
ReportErrorCount('GL-style reversed-Z, int24', QuantizeToInt24(dVals))

# OpenGL-style, infinite, reversed-Z projection matrix
zScale = -1.0
zBias = 2.0 * near
dVals = (zVals * zScale + zBias) / zVals
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('GL-style infinite reversed-Z, float32', dVals)
ReportErrorCount('GL-style infinite reversed-Z, int24', QuantizeToInt24(dVals))
'''

print('\n===== View followed by projection =====')

# Compose a x-rotation, an y-rotation, and a translation to generate a view-to-world matrix
pitch = 0.474747
yaw = 1.23123123
translation = [14.9914, 0.832148, 29.7142128]
sinPitch, cosPitch = math.sin(pitch), math.cos(pitch)
sinYaw, cosYaw = math.sin(yaw), math.cos(yaw)
viewToWorldF64 = (
	np.matrix(
		[[1, 0, 0, 0],
		 [0, cosPitch, sinPitch, 0],
		 [0, -sinPitch, cosPitch, 0],
		 [0, 0, 0, 1]],
		dtype=np.float64)
	*
	np.matrix(
		[[cosYaw, 0, sinYaw, 0],
		 [0, 1, 0, 0],
		 [-sinYaw, 0, cosYaw, 0],
		 translation + [1]],
		dtype=np.float64)
)
worldToViewF64 = viewToWorldF64.I

# Put together the Z values we're testing with some randomly generated X and Y values, and transform
# them all through the view-to-world matrix, to generate some world-space "vertex positions" that
# should have the correct depth order when seen through this view.  Note this is all done in float64
# to avoid generating roundoff errors at this stage.
yFov = math.tan(0.65)
xFov = yFov * 16.0/9.0
xValsF64 = np.random.uniform(-xFov, xFov, numVals+1).astype(np.float64) * zValsF64
yValsF64 = np.random.uniform(-yFov, yFov, numVals+1).astype(np.float64) * zValsF64
viewSpaceVertsF64 = np.column_stack((xValsF64, yValsF64, zValsF64, np.ones_like(zValsF64)))
worldSpaceVertsF64 = viewSpaceVertsF64 * viewToWorldF64

# Now bring it back down to float32 and transform back to view space
worldToViewF32 = worldToViewF64.astype(np.float32)
worldSpaceVertsF32 = worldSpaceVertsF64.astype(np.float32)
viewSpaceVertsF32 = worldSpaceVertsF32 * worldToViewF32
zVals = viewSpaceVertsF32[:,2].A1

# Control test: the unaltered z-values
ReportErrorCount('Unaltered z values, float32', zVals)
ReportErrorCount('Unaltered z values, int24', QuantizeToInt24(zVals / far))

print()

# Standard projection matrix
zScale = far / (far - near)
zBias = -near * zScale
dVals = (zVals * zScale + zBias) / zVals
ReportErrorCount('Standard projection, float32', dVals)
ReportErrorCount('Standard projection, int24', QuantizeToInt24(dVals))

# Infinite projection matrix
zScale = 1.0
zBias = -near * zScale
dVals = (zVals * zScale + zBias) / zVals
ReportErrorCount('Infinite projection, float32', dVals)
ReportErrorCount('Infinite projection, int24', QuantizeToInt24(dVals))

# Reversed-Z projection matrix
zScale = near / (near - far)
zBias = -far * zScale
dVals = (zVals * zScale + zBias) / zVals
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('Reversed-Z, float32', dVals)
ReportErrorCount('Reversed-Z, int24', QuantizeToInt24(dVals))

# Reversed-Z infinite projection matrix
zScale = 0.0
zBias = near
dVals = (zVals * zScale + zBias) / zVals
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('Infinite reversed-Z, float32', dVals)
ReportErrorCount('Infinite reversed-Z, int24', QuantizeToInt24(dVals))

print()

# OpenGL-style, standard projection matrix
zScale = (far + near) / (far - near)
zBias = -2.0 * near * far / (far - near)
dVals = (zVals * zScale + zBias) / zVals
dVals = 0.5 * dVals + 0.5	# OpenGL viewport transform
ReportErrorCount('GL-style standard, float32', dVals)
ReportErrorCount('GL-style standard, int24', QuantizeToInt24(dVals))

# OpenGL-style, infinite projection matrix
zScale = 1.0
zBias = -2.0 * near
dVals = (zVals * zScale + zBias) / zVals
dVals = 0.5 * dVals + 0.5	# OpenGL viewport transform
ReportErrorCount('GL-style infinite, float32', dVals)
ReportErrorCount('GL-style infinite, int24', QuantizeToInt24(dVals))

print('\n===== Precomposed view-projection =====')

def ComposeAndTransform(zScale, zBias):
	# Generate projection matrix (note x and y parts are irrelevant, we only look at z and w)
	projection = np.matrix(
					[[1, 0, 0, 0],
					 [0, 1, 0, 0],
					 [0, 0, zScale, 1],
					 [0, 0, zBias, 0]],
					dtype=np.float32)
	viewProj = worldToViewF32 * projection
	transformedVerts = worldSpaceVertsF32 * viewProj
	zVals = transformedVerts[:,2].A1
	wVals = transformedVerts[:,3].A1
	return zVals, zVals / wVals

# Standard projection matrix
zScale = far / (far - near)
zBias = -near * zScale
zVals, dVals = ComposeAndTransform(zScale, zBias)
ReportErrorCount('Standard projection, float32', dVals)
ReportErrorCount('Standard projection, int24', QuantizeToInt24(dVals))
GenerateHistograms('histo_02_precomposed_float32.txt', zVals, dVals)

# Infinite projection matrix
zScale = 1.0
zBias = -near * zScale
zVals, dVals = ComposeAndTransform(zScale, zBias)
ReportErrorCount('Infinite projection, float32', dVals)
ReportErrorCount('Infinite projection, int24', QuantizeToInt24(dVals))

# Reversed-Z projection matrix
zScale = near / (near - far)
zBias = -far * zScale
zVals, dVals = ComposeAndTransform(zScale, zBias)
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('Reversed-Z, float32', dVals)
ReportErrorCount('Reversed-Z, int24', QuantizeToInt24(dVals))

# Reversed-Z infinite projection matrix
zScale = 0.0
zBias = near
zVals, dVals = ComposeAndTransform(zScale, zBias)
dVals = -dVals	# Reverse the sign so the comparisons go the right way (doesn't affect precision)
ReportErrorCount('Infinite reversed-Z, float32', dVals)
ReportErrorCount('Infinite reversed-Z, int24', QuantizeToInt24(dVals))

print()

# OpenGL-style, standard projection matrix
zScale = (far + near) / (far - near)
zBias = -2.0 * near * far / (far - near)
zVals, dVals = ComposeAndTransform(zScale, zBias)
dVals = 0.5 * dVals + 0.5	# OpenGL viewport transform
ReportErrorCount('GL-style standard, float32', dVals)
ReportErrorCount('GL-style standard, int24', QuantizeToInt24(dVals))

# OpenGL-style, infinite projection matrix
zScale = 1.0
zBias = -2.0 * near
zVals, dVals = ComposeAndTransform(zScale, zBias)
dVals = 0.5 * dVals + 0.5	# OpenGL viewport transform
ReportErrorCount('GL-style infinite, float32', dVals)
ReportErrorCount('GL-style infinite, int24', QuantizeToInt24(dVals))
