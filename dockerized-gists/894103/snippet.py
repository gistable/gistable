#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import random

mappings = {
    'a': u'ä',
    'o': u'ö',
    'u': u'ü',
    'k': 'ch',
}

def _swissify_single(bit, i):
    if bit not in mappings:
        return bit
    choices = [bit] + [mappings[bit] for x in range(i)]
    return random.choice(choices)

def swissify(value, i):
    return ''.join([_swissify_single(bit, i) for bit in value])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', default=1, type=int)
    parser.add_argument('data')
    namespace = parser.parse_args()
    print swissify(namespace.data, namespace.i)
    

if __name__ == '__main__':
    main()