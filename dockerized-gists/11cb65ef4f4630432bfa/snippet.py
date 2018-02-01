# coding: utf8
import __builtin__
import keyword
import os
import tarfile
import tokenize
import zipfile
from collections import Counter


def is_python_filepath(pathname):
    return os.path.splitext(pathname)[1] == '.py'


def walkarchive(path, pathname_filter):
    if os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for name in filenames:
                if pathname_filter(name):
                    yield open(os.path.join(root, name), 'r')
    elif tarfile.is_tarfile(path):
        tf = tarfile.open(path, 'r|*')
        for info in tf:
            if pathname_filter(info.name):
                yield tf.extractfile(info)
    elif zipfile.is_zipfile(path):
        zf = zipfile.ZipFile(path)
        for name in zf.namelist():
            if pathname_filter(name):
                yield zf.open(name)
    elif pathname_filter(path):
        yield open(path, 'r')


def tokens_without_whitespaces(infile):
    tokens = tokenize.generate_tokens(infile.readline)
    for _, token, _, _, _ in tokens:
        text = token.strip()
        if text:
            yield text


def keywords():
    kws = keyword.kwlist
    blt = dir(__builtin__)
    return tuple(kws + blt)


def tokens_reserved_only(infile):
    k = keywords()
    for token in tokens_without_whitespaces(infile):
        if token in k:
            yield token


def counting_archive(filepath):
    c = Counter()
    pyfiles = walkarchive(filepath, is_python_filepath)
    for f in pyfiles:
        for token in tokens_reserved_only(f):
            c[token] += 1
    return c


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', nargs='+', help='archive filepaths.')
    p = parser.parse_args()
    counters = (counting_archive(path) for path in p.filepath)
    summary = sum(counters, Counter())
    for key, count in summary.most_common():
        print('{}\t{}'.format(key, count))
