from lxml import etree
from elasticsearch.helpers import scan
from elasticsearch import Elasticsearch
from multiprocessing import Pool
import bz2
import gensim
import itertools
import logging
import nltk
import os
import re
import string
import random
import unicodedata


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)
logging.getLogger('gensim').setLevel(logging.INFO)

tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
parser = etree.XMLParser(recover=True)
es = Elasticsearch(['localhost'])
PROCESSES = 5


def create_model():
    model = gensim.models.Doc2Vec(size=300, window=8, min_count=10, workers=16)
    model.build_vocab(sentence_generator())

    alpha, min_alpha, passes = (0.025, 0.001, 10)
    alpha_delta = (alpha - min_alpha) / passes
    for epoch in range(0, passes):
        model.alpha, model.min_alpha = alpha, alpha
        model.train(sentence_generator())
        alpha -= alpha_delta
        print('Finished epoch {}'.format(epoch))

    model.save('doc2vec_model_300_10')


def get_sentences(document):
    sentences = nltk.sent_tokenize(document['fields']['content'][0])
    sentences = [tokenize(sent) for sent in sentences]
    final = []

    for sentence_num, sentence in enumerate(sentences):
        if len(sentence) == 0:
            continue

        final.append(gensim.models.doc2vec.TaggedDocument(
            words=sentence,
            tags=['{}_{}'.format(document['_id'], sentence_num)]
        ))

    return final


def sentence_generator():
    documents = scan(
        es, index='nabu',
        scroll='30m', fields='content'
    )

    with Pool(processes=PROCESSES) as p:
        for sentences in p.imap(get_sentences, documents):
            for sentence in sentences:
                yield sentence


es_replace = re.compile(r'es$')
s_replace = re.compile(r's$')

def remove_plural(token):
    token = es_replace.sub('', token)
    token = s_replace.sub('', token)
    return token


num_replace = re.compile(r'[0-9]+')

def tokenize(sentence):
    token_list = []
    for token in tokenizer.tokenize(sentence):
        nkfd_form = unicodedata.normalize('NFKD', token)
        only_ascii = nkfd_form.encode('ASCII', 'ignore').decode('ascii')
        final = num_replace.sub('DDD', only_ascii)
        token_list.append(remove_plural(final.strip().lower()))

    return token_list

if __name__ == '__main__':
    create_model()
