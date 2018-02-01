import os.path
import collections
from operator import itemgetter

WORDFILE = '/usr/share/dict/words'

class Autocorrect(object):
    """
    Very simplistic implementation of autocorrect using ngrams.
    """
    def __init__(self, ngram_size=3, len_variance=1):
        self.ngram_size = ngram_size
        self.len_variance = len_variance

        self.words = set([w.lower() for w in open(WORDFILE).read().splitlines()])

        # create dictionary of ngrams and the words that contain them
        self.ngram_words = collections.defaultdict(set)
        for word in self.words:
            for ngram in self.ngrams(word):
                self.ngram_words[ngram].add(word)
        print "Generated %d ngrams from %d words" % (len(self.ngram_words), len(self.words))

    def lookup(self, word):
        "Return True if the word exists in the dictionary."
        return word in self.words

    def ngrams(self, word):
        "Given a word, return the set of unique ngrams in that word."
        all_ngrams = set()
        for i in range(0, len(word) - self.ngram_size + 1):
            all_ngrams.add(word[i:i + self.ngram_size])
        return all_ngrams

    def suggested_words(self, target_word, results=5):
        "Given a word, return a list of possible corrections."
        word_ranking = collections.defaultdict(int)
        possible_words = set()
        for ngram in self.ngrams(target_word):
            words = self.ngram_words[ngram]
            for word in words:
                # only use words that are within +-LEN_VARIANCE characters in 
                # length of the target word
                if len(word) >= len(target_word) - self.len_variance and \
                   len(word) <= len(target_word) + self.len_variance:
                    word_ranking[word] += 1
        # sort by descending frequency
        ranked_word_pairs = sorted(word_ranking.iteritems(), key=itemgetter(1), reverse=True)
        return [word_pair[0] for word_pair in ranked_word_pairs[0:results]]


if __name__ == '__main__':
    autocorrect = Autocorrect()
    while True:
        word = raw_input("Enter a word: ").lower()
        if autocorrect.lookup(word):
            print "Looks good to me!"
        else:
            suggestions = autocorrect.suggested_words(word)
            print "Maybe you meant: %s" % ", ".join(suggestions)
