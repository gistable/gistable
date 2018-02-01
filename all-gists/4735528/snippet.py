# -*- coding: utf-8 -*-
'''

'''
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk


def extract_entities(text):
	entities = []
	for sentence in sent_tokenize(text):
	    chunks = ne_chunk(pos_tag(word_tokenize(sentence)))
	    entities.extend([chunk for chunk in chunks if hasattr(chunk, 'node')])
	return entities


if __name__ == '__main__':
	text = """
A multi-agency manhunt is under way across several states and Mexico after
police say the former Los Angeles police officer suspected in the murders of a
college basketball coach and her fiancÃ© last weekend is following through on
his vow to kill police officers after he opened fire Wednesday night on three
police officers, killing one.
"In this case, we're his target," Sgt. Rudy Lopez from the Corona Police
Department said at a press conference.
The suspect has been identified as Christopher Jordan Dorner, 33, and he is
considered extremely dangerous and armed with multiple weapons, authorities
say. The killings appear to be retribution for his 2009 termination from the
 Los Angeles Police Department for making false statements, authorities say.
Dorner posted an online manifesto that warned, "I will bring unconventional
and asymmetrical warfare to those in LAPD uniform whether on or off duty."
"""
	print extract_entities(text)