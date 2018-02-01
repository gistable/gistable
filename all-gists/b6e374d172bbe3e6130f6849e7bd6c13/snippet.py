import nltk
import pandas as pd
import re
import pprint
import operator
import csv
import logging
from stop_words import get_stop_words
from collections import defaultdict
from gensim import corpora
from gensim.models import ldamodel
from nltk.stem import WordNetLemmatizer

# constants
STOPWORDS = set(get_stop_words('en'))
CUSTOM_STOPWORDS = {'light', 'lights', 'lights', 'sky', 'object', 'bright', 'ufo', 'quot'}
pp = pprint.PrettyPrinter(indent=4)
regex_filter = re.compile('[a-z]{2,}')
# put your custom path here if you so choose
nltk.data.path.append('')
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def tokenize_and_clean(document, stopwords=(), regex=[], lemmatizer=WordNetLemmatizer()):
    """

    :param document: a string representing a single document
    :param stopwords: a set of stopwords
    :param regex: additional regular expressions to use as a filter. Assuming these are compiled prior
    :param lemmatizer: an instance of an nltk lemmatizer
    :return: a tokenized and filtered document
    """
    raw_tokenized = nltk.tokenize.wordpunct_tokenize(document)

    tokenized = []
    for word in raw_tokenized:
        w = word.lower()
        if w not in stopwords:
            for exp in regex:
                if re.match(exp,w):
                    if lemmatizer:
                        tokenized.append(lemmatizer.lemmatize(w))
                    else:
                        tokenized.append(w)

    return tokenized


def word_frequency(corpus=[[]]):
    """

    :param corpus: a list of lists representing tokenized documents
    :return: a dict containing the frequency of each word in the corpus
    """
    frequency = defaultdict(int)
    for doc in corpus:
        for w in doc:
            frequency[w] += 1
    return dict(sorted(frequency.items(), key=operator.itemgetter(1), reverse=True))

def write_dict_to_csv(data, filepath):
    """
    Encapsulating this in a function - writes an object to a csv

    :param data: a dict containing your data
    :param filepath: the filepath for your csv file
    """
    with open(filepath, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data:
            writer.writerow([key, value])

# reading in the raw file - there are other interesting data that we won't analyze at this time
raw = pd.read_csv('./data/raw.csv', usecols=[7], names=['description'])

# a dict for our document corpus
corpus = []

for i, row in raw.iterrows():
    corpus.append(row[0])


tokenized_corpus = []
for doc in corpus:
    try:
        tokenized_corpus.append(tokenize_and_clean(document=doc, stopwords=STOPWORDS.union(CUSTOM_STOPWORDS), regex=[regex_filter]))
    except:
        pass


freq = word_frequency(tokenized_corpus)

# filtering words based off of low frequency < 10 instances (mispellings, rare words) and removing
# high frequency words that don't provide a lot of discrimination between documents
tokenized_final = [[token for token in doc if freq[token] > 10] for doc in tokenized_corpus]

# creating a vocabulary of words from this corpus for streaming use
vocabulary = corpora.Dictionary(tokenized_final)

# save to disk
vocabulary.save('data/vocabulary.dict')

print(vocabulary)

# creating an mm corpus
corpus = [vocabulary.doc2bow(text) for text in tokenized_final]
corpora.MmCorpus.serialize('data/ufo.mm', corpus)

ufo_corpus = corpora.MmCorpus('data/ufo.mm')

lda = ldamodel.LdaModel(corpus=ufo_corpus,alpha='auto', id2word=vocabulary, num_topics=20, update_every=0, passes=20)


with open('data/lda_topics', 'w') as file:
    file.write(str(lda.print_topics(-1)))

lda.print_topics(-1)