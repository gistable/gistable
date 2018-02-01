import numpy
import scipy
import matplotlib.pyplot as pyplot

def decibel(lin):
	"""Convert amplitude to decibel.
	
	We might later need power to decibel..."""
	return 20*numpy.log10(norm(lin))

def norm(sig):
	"""Normalisze signal."""
	sig_max = numpy.float(
		numpy.max(
			numpy.abs(sig)
		)
	)
	return sig / sig_max

def stft(
	x,
	fs,
	framesz,
	hop
):
	"""Short time fourier transform.

	x       : signal.
	fs      : sampling frequency.
	framesz : short time window size in seconds (y-resolution).
	hop     : window movement in seconds (x-resolution).
	"""
	framesamp = int(framesz*fs)
	hopsamp = int(hop*fs)
	w = scipy.hamming(framesamp)
	X = scipy.array([scipy.fft(w*x[i:i+framesamp])
		for i in range(
			0,
			len(x)-framesamp,
			hopsamp
		)])
	return X

def logarithmicPrune(
	spec,
	y,
	size
):
	"""Does a logarithmic prune. Removes rows from a spectrogram in a logarithmic
	fashion. It should improove performance of plotting functions. In the higher
	frequencies more rows are pruned than in the lower. Making the distribution
	of rows linear again.

	We prune the spectogram and the y-axis with the same function, in order to
	avoid mismatchs.

	spec : The spectogram to prune.
	y    : The y-axis that belongs to that spectrum.
	size : The new size of the array."""
	# Allocate lists
	speclist = size*[None]
	ylist = size*[None]
	i_max = len(spec)
	# Calculate the scaling of the indexs during prune
	# TODO: I have abosultly no idea why I need sqrt. Would be nice to
	# understand what I am doing.
	scale = (i_max) / numpy.exp(numpy.sqrt(size-1))
	index = 0
	# Slice the spectrogram and select rows.
	for i in range(0, size):
		speclist[i] = spec[int(index)].copy()
		ylist[i] = y[int(index)].copy()
		exp_val = numpy.exp(numpy.sqrt(i)) * scale
		# If the resample index didn't grow a while integer, we enforce that.
		if exp_val < (index + 1):
			index += 1
		else:
			index = int(exp_val)
	return (
		numpy.array(speclist),
		numpy.array(ylist)
	)

def spectrogram(
	data,
	fs,
	framesz=0.5,
	hop=0.01,
	yprune=600,
	fmax = None
):
	"""Display a spectrograph.

	data    : signal.
	fs      : sampling frequency.
	framesz : short time window size in seconds (y-resolution).
	hop     : window movement in seconds (x-resolution).
	yprune  : y-resolution in rows (Should be more than target the resolution).
	fmax    : Max frequency to display. Cuts the spectrogram."""
	C = stft(data, fs, framesz, hop).T
	# Set ylen from fmax if provided.
	if fmax == None:
		fmax = fs/2

	ylen = fmax/2
	# Cut the unwanted frequecies.
	C = C[1:ylen]
	# Get the len from the new array (just to be sure).
	ylen = len(C)
	# Create a linear space for the x-axis.
	x = numpy.linspace(
		0,
		len(data)/fs,
		len(C[0])
	)
	# Create logarithmic space for the y-axis.
	y = numpy.log(numpy.linspace(
		1,
		fmax,
		ylen
	))
	# Prune the the lines that are beyond resolution.
	(d, y) = logarithmicPrune(
		C,
		y,
		yprune
	);
	# Convert amplitudes to decibel
	d = decibel(numpy.absolute(d))
	# Create a meshgrid for the plotting function. This is a format conversion.
	X, Y = numpy.meshgrid(x, y);
	# Plot and set labels
	pyplot.pcolor(X, Y, d);
	pyplot.ylabel("Frequency (Hz) ");
	pyplot.xlabel('Time (seconds)');
	ax = pyplot.gca()
	liny = numpy.linspace(
		1,
		numpy.log(fmax),
		10
	)
	# Set the ticks along the log-space
	ax.set_yticks(liny)
	# The tick labes must be frequencies, so we have to invert log again.
	ax.set_yticklabels(["%.2f" % x for x in numpy.exp(liny)])
	# Colorbar with label.
	pyplot.colorbar().set_label("Amplitude (dB)")
	return C.shape
