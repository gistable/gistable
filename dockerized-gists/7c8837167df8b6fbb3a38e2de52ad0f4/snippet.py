#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script takes a BibTeX .bib file and outputs a series of .md files for use
in the Academic theme for Hugo, a general-purpose, static-site generating web
framework. Each file incorporates the data for a single publication.

Written for and tested using python 3.6.1

Requires: bibtexparser

Copyright (C) 2017 Mark Coster
"""

import argparse
import os

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bib_file", help="BibTeXfile to convert")
    parser.add_argument('dir', nargs='?', default='publication',
                        help="output directory")
    parser.add_argument("-s", "--selected", help="publications 'selected = true'",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print("Verbosity turned on")
        print("Opening {}".format(args.bib_file))

    try:
        with open(args.bib_file) as bib_file:
            parser = BibTexParser()
            parser.customization = customizations
            bib_data = bibtexparser.load(bib_file, parser=parser)
    except IOError:
        print('There was a problem opening the file.')

    if not os.path.exists(args.dir):
        if args.verbose:
            print("Creating directory '{}'".format(args.dir))
        os.makedirs(args.dir)
    os.chdir(args.dir)

    for index, entry in enumerate(bib_data.entries):
        if args.verbose:
            print("Making entry {0}: {1}".format(index + 1, entry['ID']))
        if entry['ENTRYTYPE'] != 'article':
            continue
        info = ['+++']
        abstract_clean = entry['abstract'].replace('"', '\\"')
        info.append('abstract = "{}"'.format(abstract_clean))
        info.append('abstract_short = "{}"'.format(abstract_clean))
        authors = []
        for author in entry['author']:
            authors.append('"{}"'.format(author))
        info.append('authors = [{}]'.format(', '.join(authors)))
        info.append('date = "{}-01-01"'.format(entry['year']))
        info.append('image_preview = ""')
        info.append('math = true')
        info.append('publication_types = ["2"]')
        journal_name = entry['journal']['name'].replace('\\', '')
        info.append('publication = "{}"'.format(journal_name))
        if 'volume' in entry:
            volume = entry['volume'] + ', '
        else:
            volume = ''
        info.append('publication_short = "{journal} {year}, {vol}{pages}"'.format(
            journal=journal_name,
            year=entry['year'],
            vol=volume,
            pages=entry['pages']))
        info.append('selected = {}'.format(str(args.selected).lower()))
        info.append('title = "{}"'.format(entry['title']))
        info.append('\n\n+++')
        pub_info = '\n'.join(info)
        file_name = entry['ID'] + '.md'

        try:
            if args.verbose:
                print("Saving '{}'".format(file_name))
            with open(file_name, 'w') as pub_file:
                pub_file.write(pub_info)
        except IOError:
            print('There was a problem writing to the file.')


def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = doi(record)
    record = convert_to_unicode(record)
    record = abstract(record)
    record = pages(record)
    return record


def abstract(record):
    """
    Clean abstract string.

    :param record: a record
    :type record: dict
    :return: dict -- the modified record
    """
    record['abstract'] = record['abstract'].strip(' [on SciFinder(R)]')
    return record


def pages(record):
    """
    Convert double hyphen page range to single hyphen,
    eg. '4703--4705' --> '4703-4705'

    :param record: a record
    :type record: dict
    :return: dict -- the modified record
    """
    record['pages'] = record['pages'].replace('--', '-')
    return record


if __name__ == '__main__':
    main()
