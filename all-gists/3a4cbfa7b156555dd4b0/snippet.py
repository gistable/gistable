#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random
import string
import re
from collections import Counter


def choice(words):
    random.seed
    index = random.randint(0, len(words) - 1)
    return words[index]


def test_sentence_substrings(sentence, text, n=6):
    
    words = string.split(sentence)

    groups = [words[i:i+n] for i in range(0, len(words), n)]

    for group in groups:
        group = " ".join(group)
        if group in text:
            return False

    return True


def run(text):

    text = re.sub(r'\([^)]*\)', '', text)

    words = string.split(text)

    arr = []
    end_sentence = []
    dict = {}
    prev1 = ''
    prev2 = ''
    for word in words:
        if prev1 != '' and prev2 != '':
            key = (prev2, prev1)
            if dict.has_key(key):
                dict[key].append(word)
            else:
                dict[key] = [word]
                if re.match("[\.\?\!]", prev1[-1:]):
                    end_sentence.append(key)
        prev2 = prev1
        prev1 = word

    if end_sentence == []:
        return

    key = ()
    count = 50
    max_attempts = 50000
    gtext = ""
    sentence = []
    attempts = 0

    while 1:
        if dict.has_key(key):
            word = choice(dict[key])
            sentence.append(word)
            key = (key[1], word)
            if key in end_sentence:
                sentence_str = " ".join(sentence) 
                attempts += 1
                
                # check if the beginning of sentence occurs in the text
                if sentence_str[:15] not in gtext and sentence_str not in text and test_sentence_substrings(sentence_str, text):
                    gtext += sentence_str + " "
                    count = count - 1

                sentence = []
                key = choice(end_sentence)
                if count <= 0 or attempts >= max_attempts:
                    break
        else:
            key = choice(end_sentence)
            
    return gtext

            