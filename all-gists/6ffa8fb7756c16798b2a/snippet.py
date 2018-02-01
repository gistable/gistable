# -*- coding: utf-8 -*-
from gensim.models import word2vec
import MeCab
import random
model = word2vec.Word2Vec.load("oogiri_gensim.model")
tagger = MeCab.Tagger("-Ochasen")

def word_and_kind_parse(line):
    line_word = line.split("\t")
    if len(line_word) < 2:
        return None
    w, _, _, k, _, _ = line_word
    k = k.split(u"-")[0] 
    if k == u"助詞":
        return None
    return w, k


def question(text):
    result = tagger.parse(text).decode('utf-8').split('\n')
    result = map(lambda x: x[0],
                 filter(lambda x: x,
                        [word_and_kind_parse(l) for l in result]))
    s(result)


def s(words, negative=[], recur=True):
    try:
        word_and_kind = WordManager.parse(words, negative)
        boke(word_and_kind)
        if recur:
            for word in [w for w, _ in word_and_kind]:
                s([w], [], False)
    except KeyError:
        pass


class WordManager(object):

    def __init__(self, words):
        self.set_noum(words)
        self.set_v(words)
        self.joshi = [u"の", u"は", u"が", u"を"]
        random.shuffle(self.joshi)

    def set_noum(self, words):
        self.noum = filter(lambda x: x[1] == u"名詞", words)
        random.shuffle(self.noum)
        
    def set_v(self, words):
        self.v = filter(lambda x: x[1] == u"動詞", words)
        random.shuffle(self.v)
        
    @classmethod
    def parse(self, words, negative=[]):
        most_similar = [w for w in model.most_similar(
            positive=words, negative=negative)]
        return filter(
            lambda x: x,
            [word_kind(m) for m, _ in most_similar])
        
    def choice_noum(self):
        try:
            noum = self.noum.pop()[0]
            while (noum in choiced_word):     
                noum = self.noum.pop()[0]
            choiced_word.append(noum)
            return noum
        except IndexError:
            random.shuffle(choiced_word)    
            self.set_noum(self.parse([choiced_word[0]]))
            return self.choice_noum()

    def choice_v(self):
        try:
            v = self.v.pop()[0]
            while (v in choiced_word):     
                v = self.v.pop()[0]
            choiced_word.append(v)
            return v
        except IndexError:
            seed = choiced_word + self.noum
            random.shuffle(seed)    
            self.set_v(self.parse([seed[0][0]]))
            return self.choice_v()
            
    def choice_joshi(self):
        return self.joshi.pop()


choiced_word = []
def boke(words):
    boke_pattern = [
        [u"名詞"],
        [u"名詞", u"名詞"],
        [u"名詞", u"が", u"名詞"],
        [u"名詞", u"が", u"動詞"],
        [u"名詞", u"が", u"名詞", u"な", u"名詞"],
        [u"名詞", u"が", u"名詞", u"助詞", u"動詞"],
    ]
    random.shuffle(boke_pattern)
    w = WordManager(words)
    boke_str = u""
    for word_kind in boke_pattern.pop():
        if word_kind == u"名詞":
            boke_str += w.choice_noum()
        elif word_kind == u"助詞":
            boke_str += w.choice_joshi()
        elif word_kind == u"動詞":
            boke_str += w.choice_v()
        else:
            boke_str += word_kind
    print boke_str

    
def word_kind(m):
    try:
        w, k = mecab_result(m.encode('utf-8'))
        kind = k.split(u"-")[0]
        return w, kind
    except TypeError:
        return None


def mecab_result(word):
    try:
        result = tagger.parse(word).decode('utf-8')
        w, _, _, k, _, _ = result.split(u"\t")
        return w, k
    except ValueError:
        pass


def resave():
    sentence = word2vec.Text8Corpus("oogiri_wakati.txt")
    result_model = word2vec.Word2Vec(sentence)
    result_model.save("oogiri_gensim.model")
    model = result_model
