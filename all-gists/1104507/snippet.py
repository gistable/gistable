#!/usr/bin/env python
# numpy and biopython are required -- pip install numpy biopython

from Bio import Entrez
from Bio import Medline

MAX_COUNT = 10
TERM = 'Tuberculosis'

print('Getting {0} publications containing {1}...'.format(MAX_COUNT, TERM))
Entrez.email = 'A.N.Other@example.com'
h = Entrez.esearch(db='pubmed', retmax=MAX_COUNT, term=TERM)
result = Entrez.read(h)
print('Total number of publications containing {0}: {1}'.format(TERM, result['Count']))
ids = result['IdList']
h = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
records = Medline.parse(h)

authors = []
for record in records:
    au = record.get('AU', '?')
    for a in au: 
        if a not in authors:
            authors.append(a)
    authors.sort()
print('Authors: {0}'.format(', '.join(authors)))