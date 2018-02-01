#!/usr/bin/env python
"""
Place this script in the same directory as cardxml0.unity3d, which can be
found under Hearthstone data files. Then chmod a+x and run it.

See https://eagleflow.fi/posts/2014-07-19/hearthstone-cards for more details.
"""

import re

cardxml = open('cardxml0.unity3d', 'r').read()
cards = re.findall(r'\<Entity.*?Entity\>', cardxml, re.DOTALL)
with open('cards.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>')
    for card in cards:
        f.write(card)
        f.write('\n')
