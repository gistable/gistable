from __future__ import unicode_literals
from __future__ import print_function
import sys

import plac
import bz2
import ujson
import spacy.en

def main(input_loc):
    print("Loading...")
    nlp = spacy.en.English()
    for line in bz2.BZ2File(input_loc):
        comment = ujson.loads(line)
        parse = nlp(comment['body'])
        for person in (ent for ent in parse.ents if ent.label_ == 'ORG'):
            if person.string.isspace(): # Work around a bug :(. Fixed next version.
                continue
            if person.root.dep_ == 'nsubj':
                for dobj in (w for w in person.root.head.rights if w.dep_ == 'dobj'):
                    print(person.string, person.root.head.orth_,
                          ''.join(w.string for w in dobj.subtree))

if __name__ == '__main__':
    plac.call(main)