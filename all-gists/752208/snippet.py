# Josiah Carlson - Programming Challange from Erann Gat:
# http://www.flownet.com/ron/papers/lisp-java/
# Given a list of words and a list of phone numbers, find all the ways that
# each phone number can be expressed as a list of words.

from collections import defaultdict
import sys

MAPPING = {'e':0, 'j':1, 'n':1, 'q':1, 'r':2, 'w':2, 'x':2, 'd':3, 's':3,
    'y':3, 'f':4, 't':4, 'a':5, 'm':5, 'c':6, 'i':6, 'v':6, 'b':7, 'k':7,
    'u':7, 'l':8, 'o':8, 'p':8, 'g':9, 'h':9, 'z':9}

DIGITS = set(map(str, range(10)))

def build_lookup(wordlist):
    # We're going to build a structure as follows:
    # {3 : {783: ['bo"s'], 107: ['neu'], ...}, ...}
    # This structure allows for the fast lookup of a particular phone number
    # of a given length.
    # We could have used {(3, 783): ...} instead, but creates an extra tuple
    # that is unnecessary.

    lookup = defaultdict(lambda:defaultdict(list))
    for word in wordlist:
        # Filter those digits that we care about.
        encoded = [str(MAPPING[ch]) for ch in word.lower() if ch in MAPPING]
        if not encoded:
            continue
        # We're going to exploit Python's fast int() function instead of
        # manually constructing the int ourselves.  We do this for the sake of
        # saving space, though it's probably unnecessary.
        lookup[len(encoded)][int(''.join(encoded), 10)].append(word.strip())

    return lookup

def get_numbers(number):
    # We're going to generate the lookups for possible matches from longest to
    # shortest
    x = [(0, 0)]
    for v in number:
        x.append((x[-1][0] + 1, x[-1][1] * 10 + v))
    x.reverse()
    x.pop()
    return x

def find_matches(number, lookup, already_skipped=False):
    # We're going to generate possible match lookup keys from longest to
    # shortest, then if we find a match, recurse.  If we don't find any
    # matches, we'll recurse with a digit as a filler if we've not already
    # done so at the most recent level.
    # When the recursive calls yield something of value, we'll append it to
    # what we've found, and yield what we've found.
    if not number:
        # Return the base case of an empty match, which will allow for
        # callers to add prefixes.
        yield ()
        return
    found = False
    for used_digits, value in get_numbers(number):
        # Find the matching words, if any.
        words = lookup.get(used_digits, {}).get(value, ())
        sk = not words
        found = found or bool(words)
        # If we can skip a digit, we'll try to do so now, and filter later.
        if sk and used_digits == 1 and not already_skipped and not found:
            # Use a digit as a filler.
            words = (str(value),)
        elif not words:
            # No words or not possible for a filler, skip this entry
            continue

        # As long as we can skip, or we've found a match here, we'll recurse.
        for match in find_matches(number[used_digits:], lookup, sk):
            for word in words:
                yield (word,) + match

def build_and_find_all(dictionary_file, number_file):
    lookup = build_lookup(open(dictionary_file))
    for line in open(number_file):
        line = line.strip()
        # Filter our digits...
        number = [n for n in line if n in DIGITS]
        if not number:
            continue
        # Find our matches...
        for match in find_matches(map(int, number), lookup):
            if match:
                # Properly print our matches.
                print "%s: %s"%(line, ' '.join(match))

if __name__ == '__main__':
    build_and_find_all(*sys.argv[1:])