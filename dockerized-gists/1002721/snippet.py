#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# generates text based on sample text
# 
# @author:     starenka
# @email:      'moc]tod[liamg].T.E[0aknerats'[::-1]
# @version:    1.0.3
# @since       6/1/11
# @depends     nltk, BeautifulSoup

import warnings
from urllib import urlopen
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup
import nltk

usage = "%s --h"%__file__
parser = OptionParser(usage)
parser.add_option('-s','--sample',action='store',dest='sample',default=None,
                  help='sample URL(s) f.e "http://1st http://2nd" ')
parser.add_option('-i','--input',action='store',dest='input',default=None,help='load texts from file')
parser.add_option('-b','--bigrams',action='store_true',dest='bigrams',default=False,
                  help='use bigrams instead of trigrams')
parser.add_option('-w','--words',action='store',dest='words',default=None,help='words to generate')
parser.add_option('-o','--output',action='store',dest='output',default=None,help='output file')
(options,args) = parser.parse_args()

SAMPLE_URLS = ['http://www.henryklahola.nazory.cz/Vira.htm',
               'http://www.henryklahola.nazory.cz/Snatek.htm',] \
    if not options.sample else options.sample.split(' ')
WORDS = 500 if not options.words else int(options.words)
NGRAM = 3 if not options.bigrams else 2

samples = []
if options.sample:
    for url in SAMPLE_URLS:
        sample = unicode(BeautifulSoup(urlopen(url),convertEntities=BeautifulSoup.HTML_ENTITIES))
        samples.append(nltk.clean_html(sample))
elif options.input:
    samples = [open(options.input).read().decode('utf8')]

tokenizer = nltk.tokenize.WordPunctTokenizer()
tokenized = tokenizer.tokenize(' '.join(samples))
warnings.simplefilter("ignore")
model = nltk.NgramModel(NGRAM, tokenized)

starts = model.generate(100)[-2:]
generated = model.generate(WORDS, starts)
out = ' '.join(generated).encode('utf8').replace(' , ',', ').replace(' . ','. ')
out = '%s%s...'%(out[0].upper(),out[1:])

if options.output:
    f = open(options.output,'a+')
    f.write(out)
    f.close()
else:
    print out