#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Luke Orland
# orluke@gmail.com
# Fri Apr 27 14:51:01 EDT 2012

# EXAMPLE USAGE:
# $ zcat gigaword/data/*/*gz | python gigaword-separate-sentences.py > text

# ISSUES:
# Sentence breaks are happening following the period in an abbreviation, e.g.
# Col. Mustard, Rep. Smith

import re
import sys
from bs4 import BeautifulSoup
from nltk import PunktSentenceTokenizer


replace = re.compile(r'[\n]')


def sentence_split(input_text):
    input_text = "<root>" + input_text + "</root>"

    soup = BeautifulSoup(input_text, "xml")
    paragraphs = []
    for doc in soup.find('root').findAll('DOC'):
        if doc['type'] == 'story':
            headlines = doc('HEADLINE')
            for h in headlines:
                paragraphs.append(h.contents[0])
            p_blocks = doc.find('TEXT').findAll('P')
            for p in p_blocks:
                paragraphs.append(p.contents[0])
        elif doc['type'] == 'multi':
            paragraphs.append(doc.find('TEXT').contents[0])

    sentences = []
    punkt = PunktSentenceTokenizer()
    for parag in paragraphs:
        for sent in punkt.sentences_from_text(parag, realign_boundaries=True):
            sentences.append(replace.sub(' ', sent).strip())
    return sentences


if __name__ == '__main__':
    if not sys.stdin.isatty():
        input_text = sys.stdin.read()

    sentences = sentence_split(input_text)
    for sent in sentences:
        print(unicode(sent).encode("utf-8"))

# To test, execute:
# $ nosetests gigaword-separate-sentences.py

def test_script():
    test_input = u"""
<DOC id="NYT_ENG_19990401.0001" type="story" >
<HEADLINE>
WINDS GUSTS HIT 104 MPH IN NORTHERN ARIZONA
</HEADLINE>
<DATELINE>
 (BC-WIND-ARIZ-AZR)
</DATELINE>
<TEXT>
<P>
It tipped over trucks, caused one death in a multiple-car pileup
and blew off roofs in northern Arizona. It kicked up dust so thick
in the Valley that it looked like snow.
</P>
</TEXT>
</DOC>
<DOC id="NYT_ENG_19990401.0002" type="story" >
<HEADLINE>
HAS SALMON FORGOTTEN HIS TERM PLEDGE?
</HEADLINE>
<DATELINE>
WASHINGTON (BC-TERM-LIMITS-AZR)
</DATELINE>
<TEXT>
<P>
It's hard to imagine a more ardent supporter of
congressional term limits than Rep. Matt Salmon, who was elected to
his third, presumably his final, term in November.
</P>
<P>
As a freshman in 1995, one of the Arizona Republican's first
congressional acts was to submit, with a certain flourish, a ``Six
Year Resignation Letter'' to the House clerk announcing that he
wanted his name removed from the membership rolls after his third
term expired in January 2001.
</P>
</TEXT>
</DOC>
<DOC id="AFP_ENG_19950101.0083" type="multi" >
<TEXT>
   A chronology of major world events in 1994
    PARIS, Jan 1 (AFP) - The advent of Palestinian self-rule in Gaza and in 
Jericho, the signing of peace between Israel and Jordan, continuing war in 
Bosnia and escalating bloodshed in Algeria and Rwanda were among the major 
events that marked 1994.
    JANUARY
    - Jan 1-25 - MEXICO - Between 100 and 400 people died when Indians from 
the Zapatista National Liberation Army (EZLN) stage an armed rebellion in 
Mexico's southern Chiapas state, one of the country's poorest regions. The 
rebels demanded free elections, help to combat poverty and the resignation of 
President Carlos Salinas. On June 12, EZLN fighters, after earlier talks, 
rejected government offers to end the revolt ç.
</TEXT>
</DOC>
"""
    expected = [u"WINDS GUSTS HIT 104 MPH IN NORTHERN ARIZONA",
                u"It tipped over trucks, caused one death in a multiple-car pileup and blew off roofs in northern Arizona.",
                u"It kicked up dust so thick in the Valley that it looked like snow.",
                u"HAS SALMON FORGOTTEN HIS TERM PLEDGE?",
                u"It's hard to imagine a more ardent supporter of congressional term limits than Rep.",
                u"Matt Salmon, who was elected to his third, presumably his final, term in November.",
                u"As a freshman in 1995, one of the Arizona Republican's first congressional acts was to submit, with a certain flourish, a ``Six Year Resignation Letter'' to the House clerk announcing that he wanted his name removed from the membership rolls after his third term expired in January 2001.",
                u"A chronology of major world events in 1994     PARIS, Jan 1 (AFP) - The advent of Palestinian self-rule in Gaza and in  Jericho, the signing of peace between Israel and Jordan, continuing war in  Bosnia and escalating bloodshed in Algeria and Rwanda were among the major  events that marked 1994.",
                u"JANUARY     - Jan 1-25 - MEXICO - Between 100 and 400 people died when Indians from  the Zapatista National Liberation Army (EZLN) stage an armed rebellion in  Mexico's southern Chiapas state, one of the country's poorest regions.",
                u"The  rebels demanded free elections, help to combat poverty and the resignation of  President Carlos Salinas.",
                u"On June 12, EZLN fighters, after earlier talks,  rejected government offers to end the revolt ç."]

    actual = sentence_split(test_input)
    for idx in range(len(expected)):
        print(actual[idx])
        print(expected[idx])
        assert actual[idx] == expected[idx]
    assert len(expected) == len(actual)


