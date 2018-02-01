import numpy as np

def rastaplp(signal, sr = 16000, modelorder = 8):
	# powerspectrum
	p_spectrum = powspec(signal, sr)

	# group powerspectrum to critical band
	a_spectrum = audspec(p_spectrum, sr)
	nbands = len(a_spectrum[0])

	# put in log domain
	nl_a_spectrum = np.log(a_spectrum)
	# do rasta filtering
	ras_nl_a_spectrum = rastafilt(nl_a_spectrum)
	# do inverse log
	a_spectrum = np.exp(ras_nl_a_spectrum)

	# do final auditory compressions
	post_spectrum = postaud(a_spectrum, sr) # it using sr/2 instead of sr, said ==> 2012-09-03 bug: was sr

	if modelorder > 0:
		# lpc analysis
		lpc_anal = dolpc(post_spectrum, modelorder)
		# convert lpc to cepstra
		cepstra = lpc2cep(lpc_anal, modelorder + 1)
		# or convert lpc to spectra
		spectra, F, M = lpc2spec(lpc_anal, nbands)
	else:
		# no lpc smoothing of spectrum
		spectra = post_spectrum
		cepstra = spec2cep(spectra)

	cepstra = lifter(cepstra, 0.6)

	return [cepstra, spectra, p_spectrum, lpc_anal, F, M]

def lifter(x, lift = 0.6, invs = 0):
	n_cep, nfrm = x.shape

	if lift == 0:
		y = x
	else:
		if lift > 0:
			if lift > 10:
				print("unlikely lift exponent of {} (did you mean -ve?)".format(lift))

			lift_wts = [1, ([1])]
