#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from wikitools import wiki  # https://github.com/alexz-enwp/wikitools
from wikitools import page

def search_snpedia(snp):
    """
    http://snpedia.com/index.php/Bulk
    """
    site = wiki.Wiki("http://bots.snpedia.com/api.php")
    pagehandle = page.Page(site,snp)
    snp_page = pagehandle.getWikiText()
    return snp_page

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snp', type=str, help='snp like `rs3`')
    args = parser.parse_args()

    found = search_snpedia(args.snp)
    print found

if __name__ == '__main__':
    _main()