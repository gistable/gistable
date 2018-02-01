#!/usr/bin/env python
"""
A simple command line script to count the number of records returned by an OAI-PMH provider

OAI-PMH protocol documentation: https://www.openarchives.org/OAI/openarchivesprotocol.html

To install dependencies:

  pip install lxml requests beautifulsoup4

To run, provide the base url of your OAI provider and optionally a set:

    python oaipmh-count.py http://oai.provider/url 
    python oaipmh-count.py http://oai.provider/url --set MySet:subset


"""

import argparse
import requests
from bs4 import BeautifulSoup
import sys


def get_oai_ids(oai_url, resumption_token=None, oai_set=None):
    # recursive method to

    verb = 'ListIdentifiers'
    if resumption_token is not None:
        # counting a result set with lots of resumption tokens is slow,
        # so provide output to indicate something is happening
        print '.',
        sys.stdout.flush()
        resp = requests.get(oai_url,
            params={'verb': verb, 'resumptionToken': resumption_token})
    else:
        params = {'verb': verb, 'metadataPrefix': 'oai_dc'}
        if oai_set is not None:
            params['set'] = oai_set
        resp = requests.get(oai_url, params=params)
    oaixml = BeautifulSoup(resp.content, "lxml-xml")
    token = oaixml.resumptionToken

    for record in oaixml.find_all('header'):
        # deleted oai records are returned with an attribute status="deleted":
        #    <header status="deleted">
        # yield a tuple of identifier and status
        yield (record.identifier, record.get('status'))

    # if there is a resumption token, recurse and yield the next chunk
    if token and token.string is not None:
        for result in get_oai_ids(oai_url, token.string):
            yield result


def count_oai_records(oai_url, oai_set=None):
    total = deleted = 0
    for (record, status) in get_oai_ids(oai_url, oai_set=oai_set):
        total += 1
        if status == 'deleted':
            deleted += 1

    print '\n%d total records, %d deleted records' % (total, deleted)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count results from an OAI-PMH provider')
    parser.add_argument('url', help='OAI provider base URL')
    parser.add_argument('--set', '-s', help='Count only records in the specified OAI set')
    args = parser.parse_args()
    # url is required to do anything; exit and print usage if not provided
    if not args.url:
        parser.print_help()
        exit()
    count_oai_records(args.url, oai_set=args.set)