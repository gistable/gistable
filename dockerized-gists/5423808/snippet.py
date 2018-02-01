import nltk
import string
from urllib import urlopen
from itertools import imap

url = "http://google.com"
html = urlopen(url).read()
text = nltk.clean_html(html)
text_noPunc = text.translate(string.maketrans("",""), string.punctuation)
words = text_noPunc.split()
max_word_len = max(imap(len, words))
vocabulary = nltk.probability.FreqDist(words)

for word in vocabulary:
    print word,
    print ' ' * (max_word_len + 5 - word.__len__()),
    print str(vocabulary[word])
