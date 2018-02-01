#!/usr/bin/env python2
# screamtitles.py
# ---------------

# for @inky re: https://twitter.com/inky/status/475023831770595328

from __future__ import division

import sys
import codecs
import re
import random
import math

# how many subtitles should be replaced with...whatever
percentage = 0.1

# other non-screaming sound effects!
screams = ('[screaming]',)

class Subtitle:
    def __init__(self, raw_text):
        raw_lines = list(map(lambda x: x.strip(), raw_text.split('\n')))
        self.s_id = raw_lines[0]
        self.time = raw_lines[1]
        self.text = raw_lines[2:]

    def __str__(self):
        return '\n'.join((self.s_id, self.time, '\n'.join(self.text)))

    def __repr__(self):
        return 'Subtitle(' + self.__str__() + ')'
    
def parse_subtitle_list(raw_text):
    split_text = re.split('\r?\n\r?\n', raw_text)
    return list(map(lambda x: Subtitle(x), split_text))

if __name__ == '__main__': 
    input_subs = sys.argv[1]

    with codecs.open(input_subs, encoding='utf-8') as f:
        raw_text = f.read().strip().replace('\ufeff', '')

    split_text = re.split('\r?\n\r?\n', raw_text)
    subs = [Subtitle(x) for x in split_text]

    replace_sub_ids = random.sample(range(len(subs)), int(math.floor(percentage * len(subs))))

    for s_id in replace_sub_ids:
        subs[s_id].text = [random.choice(screams)]

    with codecs.open(input_subs + '.bak', 'w', encoding='utf-8') as f:
        f.write(raw_text)

    with codecs.open(input_subs, 'w', encoding='utf-8') as f:
        for sub in subs:
            f.write(str(sub) + '\n\n')

    print('screamysubs in {0}, original subs saved to {0}.bak'.format(input_subs))
