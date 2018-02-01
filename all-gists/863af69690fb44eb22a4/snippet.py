#!/usr/bin/env python
from __future__ import print_function, division
import argparse
import json
import sys
from gzip import GzipFile


def concat_claims(claims):
    for rel_id, rel_claims in claims.iteritems():
        for claim in rel_claims:
            yield claim


def to_triplets(ent):
    claims = concat_claims(ent['claims'])
    triplets = []
    e1 = ent['id']
    for claim in claims:
        mainsnak = claim['mainsnak']
        if mainsnak['snaktype'] != "value":
            continue
        if mainsnak['datatype'] == 'wikibase-item':
            rel = mainsnak['property']
            e2 = 'Q{}'.format(mainsnak['datavalue']['value']['numeric-id'])
            triplets.append((e1, rel, e2))
    return triplets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Log-Bilinear model for relation extraction.')
    _arg = parser.add_argument
    _arg('--read-dump', type=str, action='store',
         metavar='PATH', help='Reads in a wikidata json dump.')
    args = parser.parse_args()

    train_set = None
    if args.read_dump:
        dump_in = GzipFile(args.read_dump, 'r')
        line = dump_in.readline();
        iter = 0
        while line != '':
            iter += 1
            line = dump_in.readline()
            try:
                ent = json.loads(line.rstrip('\n,'))
                if not ent['id'].startswith('Q'):
                    print("Skipping item with id {}".format(ent['id']),
                          file=sys.stderr)
                    continue
                print('\n'.join(
                    ['{}\t{}\t{}'.format(*t) for t in to_triplets(ent)]),
                      file=sys.stdout)
            except (KeyError, ValueError) as e:
                print(e, file=sys.stderr)
            if iter % 1000 == 0:
                sys.stdout.flush()
