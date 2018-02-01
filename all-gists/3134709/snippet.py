'''
Command line script used to grab synonyms off the web using a thesaurus api.

The words come from the "Big Huge Thesaurus", and I make no claims about the 
results. In order to use this script you will need a valid API key, which is
available, for free (up to 10,000 calls / day), from here - http://words.bighugelabs.com/getkey.php
If you're really lazy, you can just use my key - eb4e57bb2c34032da68dfeb3a0578b68
but I'd rather you didn't. Thanks.

Examples:

python thesaurus.py sad
python thesaurus.py sad happy
python thesaurus.py sad --out file.txt
python thesaurus.py sad --key eb4e57bb2c34032da68dfeb3a0578b68

Created: 17-July-2012
Author: Hugo Rodger-Brown

'''
import sys
import json
import requests
import argparse
from os import path

API_KEY = '<your_key_goes_here>' # API key is available from here - http://words.bighugelabs.com/getkey.php
URL_MASK = 'http://words.bighugelabs.com/api/2/{1}/{0}/json'
RELATIONSHIP_ABBR = {'syn':'Synonyms','ant':'Antonyms','rel':'Related terms','sim':'Similar terms','usr':'User suggestions'}
VALID_FILE_EXTENSIONS = ['.txt','.csv','.json','.js']

def lookup_word(word):
    ''' Performs the lookup of a given word against the thesaurus API 

    :param word: the word to look up
    :returns: all matching synonyms, antonyms, related terms, similar terms and user suggestions
    
    '''

    url = URL_MASK.format(word, API_KEY)

    r = requests.get(url)
    j = json.loads(r.text)

    if not j.get('adjective'):
        print 'This is not an adjective.'
        return

    for rel in j['adjective']:
        print '{0}: {1}'.format(RELATIONSHIP_ABBR[rel], j['adjective'][rel])
        for w in j['adjective'][rel]:
            yield w,rel

parser = argparse.ArgumentParser(description='Use online thesaurus to look up synonyms, antonyms etc.')
parser.add_argument('words', action='store', help='words to look up in the thesaurus (space delimited)', nargs='+')
parser.add_argument('--out','-o', action='store', help='If set then the output will be written to a file. Output format is set from the file extension [.json|.csv]')
parser.add_argument('--key','-k', action='store', help='If set will override the API_KEY value in the script, and be used to authenticate API calls.')
args = parser.parse_args()

if args.key:
    API_KEY = args.key
elif API_KEY == '<your_key_goes_here>':
    raise Exception('Invalid API_KEY - test keys are available from http://words.bighugelabs.com/getkey.php')
    sys.exit()

d = dict()
for word in args.words:
    print '\nLooking up words related to \'{0}\'\n'.format(word)
    for related_word,relationship in lookup_word(word):
        if relationship != 'ant': # ignore antonyms from the output
            d.update({related_word:word})

print '\nDictionary of all words:\n'
print '[{0}]\n'.format(d)

# args.out contains the output filename
if args.out is not None:

    fileName, fileExtension = path.splitext(args.out)
    
    if fileExtension not in VALID_FILE_EXTENSIONS:
        print 'Invalid file format - must be [txt|csv|json|js]'
        sys.exit()

    with open(args.out, 'w') as f:
        if fileExtension in ['.csv','.txt']:
            for t in d:
                f.write('{0},{1}\n'.format(t,d[t]))
        elif fileExtension in ['.json','.js']:
            f.write('[{0}]'.format(d))

    print '\nResults have been written to {0}'.format(args.out)