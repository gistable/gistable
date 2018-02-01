"""Extract several BOW models from a corpus of text files.

The models are stored in Matrix Market format which can be read
by gensim. The texts are read from .txt files in the directory
specified as TOPDIR. The output is written to the current directory."""
# NB: All strings are utf8 (not unicode).
import os
import glob
import nltk
import gensim

# A directory with .txt files
TOPDIR = '../texts/'


def iterdocuments(topdir):
	"""Iterate over documents, yielding a list of utf8 tokens at a time."""
	for filename in sorted(glob.glob(os.path.join(topdir, '*.txt'))):
		with open(filename) as fileobj:
			document = fileobj.read()
		name = os.path.basename(filename)
		if isinstance(name, unicode):
			name = name.encode('utf8')
		tokenized = gensim.utils.tokenize(document, lowercase=True)
		yield name, tokenized


def ngrams(tokens, n):
	"""Turn a sequence of tokens into space-separated n-grams."""
	if n == 1:
		return tokens
	return (' '.join(a) for a in nltk.ngrams(tokens, n))


class ChunkedCorpus(object):
	"""Split text files into chunks and extract n-gram BOW model."""
	def __init__(self, topdir, chunksize=5000, ngram=1, dictionary=None):
		self.topdir = topdir
		self.ngram = ngram
		self.chunksize = chunksize
		self.chunknames = []
		if dictionary is None:
			self.dictionary = gensim.corpora.Dictionary(
					ngrams(tokens, ngram)
					for _, tokens in iterdocuments(topdir))
			self.dictionary.filter_extremes(no_below=5, keep_n=2000000)
			self.dictionary.compactify()
		else:
			self.dictionary = dictionary

	def __iter__(self):
		for filename, tokens in iterdocuments(self.topdir):
			for n, chunk in enumerate(gensim.utils.chunkize(
					ngrams(tokens, self.ngram),
					self.chunksize,
					maxsize=2)):
				self.chunknames.append('%s_%d' % (filename, n))
				yield self.dictionary.doc2bow(chunk)


def main():
	# Example: extract unigram and bigram models
	# from texts divided into chunks of 1000 and 5000 tokens.
	unigram1000 = ChunkedCorpus(TOPDIR, chunksize=1000, ngram=1)
	unigram1000.dictionary.save('unigram.dict')
	unigram5000 = ChunkedCorpus(TOPDIR, chunksize=5000, ngram=1,
			dictionary=unigram1000.dictionary)
	gensim.corpora.MmCorpus.serialize('unigram1000.mm', unigram1000)
	with open('chunks1000.filenames', 'w') as out:
		out.writelines(b'%s\n' % name for name in unigram1000.chunknames)
	gensim.corpora.MmCorpus.serialize('unigram5000.mm', unigram5000)
	with open('chunks5000.filenames', 'w') as out:
		out.writelines(b'%s\n' % name for name in unigram5000.chunknames)

	bigram1000 = ChunkedCorpus(TOPDIR, chunksize=1000, ngram=2)
	bigram1000.dictionary.save('bigram.dict')
	bigram5000 = ChunkedCorpus(TOPDIR, chunksize=5000, ngram=2,
			dictionary=bigram1000.dictionary)
	gensim.corpora.MmCorpus.serialize('bigram1000.mm', bigram1000)
	gensim.corpora.MmCorpus.serialize('bigram5000.mm', bigram5000)

if __name__ == '__main__':
	main()