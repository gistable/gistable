"""
This file contains python functions for automatically retreiving DOI metadata
and creating bibtex references. `get_bibtex_entry(doi)` creates a bibtex entry
for a DOI. It fixes a Data Cite author name parsing issue. Short DOIs are used
for bibtex citation keys.

Created by Daniel Himmelstein and released under CC0 1.0.
"""

import urllib.request

import requests
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase

def shorten(doi, cache={}, verbose=False):
    """
    Get the shortDOI for a DOI. Providing a cache dictionary will prevent
    multiple API requests for the same DOI.
    """
    if doi in cache:
        return cache[doi]
    quoted_doi = urllib.request.quote(doi)
    url = 'http://shortdoi.org/{}?format=json'.format(quoted_doi)
    try:
        response = requests.get(url).json()
        short_doi = response['ShortDOI']
    except Exception as e:
        if verbose:
            print(doi, 'failed with', e)
        return None
    cache[doi] = short_doi
    return short_doi

def get_bibtext(doi, cache={}):
    """
    Use DOI Content Negotioation (http://crosscite.org/cn/) to retrieve a string
    with the bibtex entry.
    """
    if doi in cache:
        return cache[doi]
    url = 'https://doi.org/' + urllib.request.quote(doi)
    header = {
        'Accept': 'application/x-bibtex',
    }
    response = requests.get(url, headers=header)
    bibtext = response.text
    if bibtext:
        cache[doi] = bibtext
    return bibtext

def get_bibtex_entry(doi, bibtext_cache={}, shortdoi_cache={}):
    """
    Return a bibtexparser entry for a DOI
    """
    bibtext = get_bibtext(doi, cache = bibtext_cache)
    if not bibtext:
        return None

    short_doi = shorten(doi, cache = shortdoi_cache)
    parser = BibTexParser()
    parser.ignore_nonstandard_types = False
    bibdb = bibtexparser.loads(bibtext, parser)
    entry, = bibdb.entries
    quoted_doi = urllib.request.quote(doi)
    entry['link'] = 'https://doi.org/{}'.format(quoted_doi)
    if 'author' in entry:
        entry['author'] = ' and '.join(entry['author'].rstrip(';').split('; '))
    entry['ID'] = short_doi[3:]
    return entry

def entries_to_str(entries):
    """
    Pass a list of bibtexparser entries and return a bibtex formatted string.
    """
    db = BibDatabase()
    db.entries = entries
    return bibtexparser.dumps(db)
