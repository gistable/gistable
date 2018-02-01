# -*- coding: utf-8 -*-
'''
Turkish POS Tagger
Author: Sirin Saygili <sirin.neslihan@gmail.com>
Turkish POS Tagger is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Turkish POS Tagger is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Turkish POS Tagger.  If not, see <http://www.gnu.org/licenses/>.
'''

import random
import yaml
from nltk import tag
from nltk.tag import brill
from nltk.tag.brill import Template
from nltk.tag.brill_trainer import BrillTaggerTrainer
from nltk.corpus.reader import ConllCorpusReader
import codecs
from datetime import datetime

class TurkishPosTagger():

    def __init__(self):
        self.sentences = self.read_turkish_corpus()
        random.seed(len(self.sentences))
        random.shuffle(self.sentences)
        self.sentences = self.sentences
        self.max_rules = 300
        self.min_score = 3
        self.development_size = len(self.sentences)
        self.train_size = 0.85
        self.re_tagger = tag.RegexpTagger([(r'^-?[0-9]+(.[0-9]+)?$', 'PUNC'), (r'.*', 'NOUN_NOM')])

    def read_turkish_corpus(self):
        tagged_sentences_raw = []
        conll_reader = ConllCorpusReader('path/to/languages-corpora', 'path/to/turkish-pos-conll-file', ('words','pos'), encoding='UTF-8')
        tagged_sentences_raw_map = conll_reader.tagged_sents('path/to/turkish-pos-conll-file')
        for sent in tagged_sentences_raw_map:
            tagged_sentences_raw.append(sent)
        tagged_sentences = [[(w.lower(),t) for (w,t) in s] for s in tagged_sentences_raw]
        return tagged_sentences

    def randomize_sentences(self):
        random.seed(len(self.sentences))
        random.shuffle(self.sentences)

    def get_cutoff(self):
        return int(self.development_size * self.train_size)

    def set_train_set(self, cutoff):
        return self.sentences[:cutoff]

    def set_evaluation_set(self, cutoff, size):
        return self.sentences[cutoff:size]

    def dump_tagger_to_file(self, tr_tagger):
        f = codecs.open('tr-tagger.yaml', mode='w', encoding='UTF-8')
        yaml.dump(tr_tagger, f)
        f.close()

    def turkish_unigram_tagger(self, train_data, eval_data, backoff_tagger):
        tr_unigram_tagger = tag.UnigramTagger(train_data, backoff=backoff_tagger)
        print "TR unigram accuracy: %s" % tr_unigram_tagger.evaluate(eval_data)
        return tr_unigram_tagger

    def turkish_bigram_tagger(self, train_data, eval_data, backoff_tagger):
        tr_bigram_tagger = tag.BigramTagger(train_data, backoff=backoff_tagger)
        print "TR bigram accuracy: %s" % tr_bigram_tagger.evaluate(eval_data)
        return tr_bigram_tagger

    def turkish_trigram_tagger(self, train_data, eval_data, backoff_tagger):
        tr_trigram_tagger = tag.BigramTagger(train_data, backoff=backoff_tagger)
        print "TR trigram accuracy: %s" % tr_trigram_tagger.evaluate(eval_data)
        return tr_trigram_tagger

    def turkish_brill_tagger(self):

        train_data = self.set_train_set(self.get_cutoff())
        eval_data = self.set_evaluation_set(self.get_cutoff(), self.development_size)

        tr_unigram = self.turkish_unigram_tagger(train_data, eval_data, self.re_tagger)
        tr_bigram = self.turkish_bigram_tagger(train_data, eval_data, tr_unigram)
        tr_trigram = self.turkish_trigram_tagger(train_data, eval_data, tr_bigram)

        templates = [
            Template(brill.Pos, (1,1)),
            Template(brill.Pos, (2,2)),
            Template(brill.Pos, (1,2)),
            Template(brill.Pos, (1,3)),
            Template(brill.Word, (1,1)),
            Template(brill.Word, (2,2)),
            Template(brill.Word, (1,2)),
            Template(brill.Word, (1,3)),
            Template(brill.Pos, (-1, -1), (1,1)),
            Template(brill.Pos, (-1, -1), (1,1)),
        ]

        br_trainer = BrillTaggerTrainer(tr_trigram, templates)
        tr_brill_tagger = br_trainer.train(train_data, self.max_rules, self.min_score)
        print "TR initial Brill accuracy: %s" % tr_brill_tagger.evaluate(eval_data)

        for i in range(1,5):
            self.randomize_sentences()
            training_data = self.set_train_set(self.get_cutoff())
            evaluation_data = self.set_evaluation_set(self.get_cutoff(), self.development_size)
            print 'Fold: %s' % i
            tr_brill_tagger = br_trainer.train(training_data, self.max_rules, self.min_score)
            print "TR Brill accuracy: %s" % tr_brill_tagger.evaluate(evaluation_data)

        self.dump_tagger_to_file(tr_brill_tagger)

class TRTagger():

    def read_tagger(self):
        f = codecs.open('tr-tagger.yaml',mode='r',encoding='UTF-8')
        tr_pos_tagger = yaml.load(f)
        return tr_pos_tagger

    def turkish_pos_tagger(self, sentence):
        temp = [[t.lower()] for t in sentence.split()]
        return_list = []
        # Find tags
        tr_pos_tagger = self.read_tagger()
        for token in temp:
            return_list.append(tr_pos_tagger.tag(token))

        return_list = [t for [t] in return_list]
        # Correct tags for printing
        tag_list = [y for (x,y) in return_list]
        tag_list = [(y.lower()).title() for y in tag_list]

        # Zip input and tags
        temp_list = zip([t for t in sentence.split()], tag_list)
        return temp_list


#TrTagger = TurkishPosTagger()
#tr_b = TrTagger.turkish_brill_tagger()

if __name__ == '__main__':
    sent = "Uzun bir süre sonra kendime geldim ."
    decoded_sent = sent.decode('utf-8')
    tr_brill = TRTagger()
    print tr_brill.turkish_pos_tagger(decoded_sent)
    # output is "uzun-Adj bir-Det süre-Noun sonra-Adv kendime-Pron geldim-Verb .-Punc"