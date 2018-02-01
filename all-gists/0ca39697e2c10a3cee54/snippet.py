#!/usr/bin/env python
# altwords.py
# kashev - kashev.dalmia@gmail.com
# https://gist.github.com/kashev/0ca39697e2c10a3cee54

""" Script to generate words of a specified length that alternate
    hands on a QWERTY keyboard. For use in generating passwords that
    are pleasant to type.
"""

# FUTURE IMPORTS
from __future__ import division
from __future__ import print_function

# IMPORTS
import argparse
import os

# CONSTANTS
KEYS_LEFT = set("qwertasdfgzxcvb")
KEYS_RIGHT = set("yuiophjklnm")
DICTIONARY_FILE = os.path.join('/usr', 'share', 'dict', 'words')


def find_words(length):
    """ Given a word length, find all alternating words of that length. """

    with open(DICTIONARY_FILE, 'r') as dfile:
        ret = []
        for line in dfile:
            word = line.split()[0].lower()
            if len(word) != length:
                continue
            # Case 1: First letter is in left hand
            if word[0] in KEYS_LEFT:
                add = True
                for i in range(length):
                    if i % 2 == 0 and word[i] not in KEYS_LEFT:
                        add = False
                        continue
                    if i % 2 == 1 and word[i] not in KEYS_RIGHT:
                        add = False
                        continue
                if add:
                    ret.append(word)
            # Case 2: First letter is in right hand
            else:
                add = True
                for i in range(length):
                    if i % 2 == 0 and word[i] not in KEYS_RIGHT:
                        add = False
                        continue
                    if i % 2 == 1 and word[i] not in KEYS_LEFT:
                        add = False
                        continue
                if add:
                    ret.append(word)

        return ret


def main():
    """ Main function run when the script is called from the command line. """
    parser = argparse.ArgumentParser(description="Print a list of words whose "
                                                 "letters alternate hands on "
                                                 "the keyboard of a specified "
                                                 "length.")
    parser.add_argument('length',
                        metavar='N',
                        type=int,
                        nargs=1,
                        help="the length of desired words")

    args = parser.parse_args()
    length = args.length[0]

    print(find_words(length))


if __name__ == '__main__':
    main()
