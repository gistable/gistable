from pylab import *
from scipy.ndimage import measurements
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import signal

def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
 
# Set up the figures
plt.figure(0, figsize=(9,9))
plt.title("Clusters by area")

plt.figure(1, figsize=(7,4))
plt.title("Number of clusters")

plt.figure(2, figsize = (7,4))
plt.title("Largest Cluster")
plt.ion()

time.sleep(20)
 
for L in [50, 100, 200, 500, 1000]: 

  for marker in ['ko', 'bo', 'ro']:
		# Randomise the percolation network
		r = rand(L,L)
	 
		for p in np.arange(0., 1., 0.05):
			# Determine the connectivity for probability p
			z = r<p

			# Define the clusters using the ndimage.measurements routines
			lw, num = measurements.label(z)

			# Plot the clusters for given p
			plt.figure(0)
			area = measurements.sum(z, lw, index=arange(lw.max() + 1))
			areaImg = area[lw]
			plt.imshow(areaImg, origin='lower', interpolation='nearest', vmin=1, vmax=L*5)
			plt.draw()

			# Plot the number of clusters		
			plt.figure(1)
			plt.plot(p, lw.max(), marker)
			plt.draw()

			# Plot the size of the largest cluster		
			plt.figure(2)
			plt.plot(p, area.max(), marker)
			plt.draw()
		plt.ioff() 
		plt.show()

