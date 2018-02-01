from collections import defaultdict
import fileinput
import random
import re

common = """the of and to a in for is on that by this with
i you it not or be are from at as your all have an was we
will can us i'm it you're i've my of""".split()

pronounce = {}
# Load pronunciations from the CMU pronunciation dictionary.
# Data: https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
with open('cmudict.dict') as f:
    for line in f:
        word, *phonemes = line.strip().split(' ')
        pronounce[word] = phonemes

def vowel_key(phonemes):
    '''
    Return the 'vowel key' for a list of phonemes.

    Example: for both the pronunciations of 'shining' and 'typist'
    this is ('AY1', 'IH0'), so these words are said to 'sound the same.'
    '''
    return tuple(x for x in phonemes if x[:1] in 'AEIOU')

# Create a literal rhyming dictionary!
# rhymes[('AY1', 'IH0')] contains 'shining', 'typist', 'whitish'...
rhymes = defaultdict(list)
for k, v in pronounce.items():
    rhymes[vowel_key(v)].append(k)

def find_rhyme(word):
    '''Return a random word that sounds like the given word.'''

    # Don't change really common/short words, or ones we don't know.
    lword = word.lower()
    if lword in common or len(lword) <= 3 or lword not in pronounce:
        return word

    # Pick a random rhyme: a word with the same vowel key as this one.
    rhyme = random.choice(rhymes[vowel_key(pronounce[lword])])

    # Remove parenthesized numbers from the end of the rhyme.
    # (This is just how cmudict lists alternate pronunciations.)
    rhyme = re.sub(r'\(\d+\)$', '', rhyme)

    # Restore capitalization from the original.
    if word[:1].isupper():
        rhyme = rhyme[:1].upper() + rhyme[1:]

    return rhyme

def rhyme_each_word(line):
    return re.sub(r"[\w']+", lambda m: find_rhyme(m.group(0)), line.strip())

if __name__ == '__main__':
    for l in fileinput.input():
        print(rhyme_each_word(l))
