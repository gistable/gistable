from xml.etree import ElementTree as ET
import urllib
import os
import itertools, random

plus = "%2B"
neg = "-"

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def shuffle(name):
  namelist = ["".join(perm) for perm in itertools.permutations(name)]
	random.shuffle(namelist)
	return str(namelist[len(name)])

'''
This method is the bit that actually uses Metaphor Magnet. It asks for metaphors that map
the patron creature onto the target occupation. So 'thieves as spiders' asks for qualities
of spiders that have potential mappings onto thieves. It will return an adjective:noun pair.

NOTE THAT the noun is not necessarily 'spider' in this case. If it finds a property that
spiders have, e.g. being quick, it may decide that a better noun represents that property.
It is still making the metaphorical connection between properties of spiders and thieves,
but it may actually return Quick Tiger. You could always ditch the noun and replace it
with the patron if you wished.

There are *loads* more uses for Metaphor Magnet. I'm going to keep hacking at it!
'''
def produceName(target, patron):
	URL = 'http://ngrams.ucd.ie/metaphor-magnet-acl/q?kw='+target+'+as+'+patron+'&xml=true'

	# connect to a URL, and that URL will return a number like 1200.
	xmldata = str(urllib.urlopen(URL).read())

	f = ET.XML(xmldata)


	for element in f:
	    if element.tag == "Target":
	    	metaphor = element[0].text.split()[0]
	        metaphor_adj = (str(metaphor).split(':')[0]);
	        metaphor_tgt = (str(metaphor).split(':')[1]);
	        break;

	return ("The "+metaphor_adj.capitalize()+" "+metaphor_tgt.capitalize())

print(shuffle("thieves").capitalize()+", "+produceName("thieves", plus+"spiders"))
print(shuffle("priests").capitalize()+", "+produceName("priests", "doves"))
print(shuffle("hunters").capitalize()+", "+produceName("hunters", "tigers"))