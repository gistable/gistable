#!/usr/bin/env python
# encoding: utf-8

import sys
import csv
import json
from collections import OrderedDict

LVLS_MAP = {
    '0': 'cantrip',
    '1': '1st-level',
    '2': '2nd-level',
    '3': '3rd-level',
    '4': '4th-level',
    '5': '5th-level',
    '6': '6th-level',
    '7': '7th-level',
    '8': '8th-level',
    '9': '9th-level',
}

CLASSES = {
    'BRD': 'bard',
    'CLR': 'cleric',
    'DRU': 'druid',
    'PAL': 'paladin',
    'RNG': 'ranger',
    'SOR': 'sorcerer',
    'WAR': 'warlock',
    'WIZ': 'wizard',
}

OUTPUT_ORDER = [
        'title',
        'contents',
        'tags',
        'color',
        'icon',
        'icon_back',
        'title_size',
        'count',
]

cards_f = open(sys.argv[1], 'r+')
database_f = open(sys.argv[2], 'r+')

cards = json.load(cards_f)

database = {}
reader = csv.DictReader(database_f)
for row in reader:
    database[row['SPELL']] = row

for card in cards:

    if card['title'] in database:
        db_entry = database[card['title']]
    else:
        for trans in [('/', ' and '), ('/', ' or '), ('&', 'and'),
                      ('from', 'From'), ('with', 'With'),
                      ('MK\'s', 'Mordenkainen\'s')]:
            new_title = card['title'].replace(*trans)
            if new_title in database:
                db_entry = database[new_title]
                break
        else:
            print('WARNING: Could not match %s' % card['title'],
                  file=sys.stderr)
            continue

    if 'spell' not in card['tags']:
        card['tags'].insert(0, 'spell')

    if LVLS_MAP[db_entry['LVL']] not in card['tags']:
        card['tags'].insert(1, LVLS_MAP[db_entry['LVL']])

    card['icon_back'] = 'white-book-%s' % db_entry['LVL']

    if db_entry['Ritual?']:
        if 'ritual' not in card['tags']:
            card['tags'].insert(2, 'ritual')

    for db_class, card_class in CLASSES.items():
        if db_entry[db_class]:
            if card_class not in card['tags']:
                card['tags'].append(card_class)

    # tmps = sorted(card.items(), key=lambda x, y: 1)


cards = [OrderedDict(sorted(card.items(),
                     key=lambda kv: OUTPUT_ORDER.index(kv[0])))
         for card in cards]


print(json.dumps(cards, indent=2))