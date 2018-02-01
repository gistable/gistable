#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os.path
import bz2

from gensim.corpora import WikiCorpus
from gensim.corpora.wikicorpus import filterWiki
import MeCab

logger = logging.getLogger('jawikicorpus')
logger.setLevel(logging.INFO)

tagger = MeCab.Tagger()

DEFAULT_DICT_SIZE = 100000
ARTICLE_MIN_CHARS = 500

def jatokenize(text):
    node = tagger.parseToNode(text.encode('utf-8')).next
    while node:
        if node.feature.split(',')[0] == '名詞':
            yield node.surface.lower()
        node = node.next

def tokenize(content):
    return [token for token in jatokenize(content) if not token.startswith('_')]

class JaWikiCorpus(WikiCorpus):
    def getArticles(self, return_raw=False):
        articles, articles_all = 0, 0
        intext, positions = False, 0
        for lineno, line in enumerate(bz2.BZ2File(self.fname)):
            if line.startswith('      <text'):
                intext = True
                line = line[line.find('>') + 1 : ]
                lines = [line]
            elif intext:
                lines.append(line)
            pos = line.find('</text>') # can be on the same line as <text>
            if pos >= 0:
                articles_all += 1
                intext = False
                if not lines:
                    continue
                lines[-1] = line[:pos]
                text = filterWiki(''.join(lines))
                if len(text) > ARTICLE_MIN_CHARS: # article redirects are pruned here
                    articles += 1
                    if return_raw:
                        result = text
                    else:
                        result = tokenize(text) # text into tokens here
                        positions += len(result)
                    yield result

        logger.info("finished iterating over Wikipedia corpus of %i documents with %i positions"
                     " (total %i articles before pruning)" %
                     (articles, positions, articles_all))
        self.numDocs = articles # cache corpus length

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logging.info("running %s" % ' '.join(sys.argv))
    program = os.path.basename(sys.argv[0])
    if len(sys.argv) < 3:
        print globals()['__doc__'] % locals()
        sys.exit(1)
    input, output = sys.argv[1:3]
    if len(sys.argv) > 3:
        keep_words = int(sys.argv[3])
    else:
        keep_words = DEFAULT_DICT_SIZE
    wiki = JaWikiCorpus(input, keep_words=keep_words)
    wiki.saveAsText(output)
    del wiki
    from gensim.corpora import MmCorpus
    id2token = JaWikiCorpus.loadDictionary(output + '_wordids.txt')
    mm = MmCorpus(output + '_bow.mm')
    from gensim.models import TfidfModel
    tfidf = TfidfModel(mm, id2word=id2token, normalize=True)
    MmCorpus.saveCorpus(output + '_tfidf.mm', tfidf[mm], progressCnt=10000)
    logging.info("finished running %s" % program)