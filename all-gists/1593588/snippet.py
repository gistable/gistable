def word_freq(word, section):
	freq = nltk.probability.FreqDist(nltk.corpus.brown.words(categories = section))
	word_frequency = freq[word]
	return word_frequency