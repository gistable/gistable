#! /usr/bin/env python
# -*- coding:utf-8 -*-

import concurrent.futures
import sys
import subprocess
import time
from collections import defaultdict
from data import sentences


def sent2kgram(sentence, k=2, delimiter=" "):
    sentence = str(subprocess.getoutput("echo %s | mecab -O wakati" % (sentence)))
    words = sentence.strip().split()
    length, kgrams = len(words), []
    for i in range(length - k):
        kgram = delimiter.join(words[i:i + k])
        kgrams.append(kgram)
    return kgrams


def timef(f):
    def wrapper():
        start = time.time()
        f()
        end = time.time()
        print("%s: %.2fms" % (f.__name__, (end - start) * 1000))
    return wrapper


@timef
def single_process():
    kgram2id = defaultdict(lambda: len(kgram2id))
    for sentence in sentences:
        kgram = sent2kgram(sentence)
        kgram = map(lambda x: kgram2id[x], kgram)
    return kgram2id


@timef
def multi_process():
    kgram2id = defaultdict(lambda: len(kgram2id))
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        for res_kgram in executor.map(sent2kgram, sentences):
            res_kgram = map(lambda x: kgram2id[x], res_kgram)
    return kgram2id


def main():
    single_process()
    multi_process()

if __name__ == "__main__":
    main()
