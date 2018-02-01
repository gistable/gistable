#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#                                              #
# Script to download entire animorphs series   #
#                                              #
# Usage: python animorphs-downloader.py --help #
#                                              #
#################################################

import os
from urllib2 import urlopen, quote

URL = 'http://downloads.animorphsforum.com/books/pdf/'

ORIGINAL_SERIES = [ "%02d" % number for number in range(1, 55)]
MEGAMORPHS = ['Megamorphs1', 'Megamorphs2', 'Megamorphs3', 'Megamorphs4']
OTHERS = ['Andalite', 'Ellimist', 'Visser', 'Hork-Bajir', 'Alternamorphs01', 'Alternamorphs02', 'Vegemorphs']
OK = 200

BOOKS = ORIGINAL_SERIES + MEGAMORPHS + OTHERS

def get_book_details():
    """ Construct urls for each book"""
    for book in BOOKS:
        book = book + ".pdf"
        url = URL + book
        yield url, book

def get_or_create_animorphs_dir():
    cwd = os.getcwd()
    animorphs_dir = os.path.join(cwd, 'animorphs')
    if not os.path.exists(animorphs_dir):
        print "Creating animorphs directory..."
        os.mkdir(animorphs_dir)
    return animorphs_dir

def download_book(url, book):
    book_path = os.path.join(get_or_create_animorphs_dir(), book)
    try:
        print "Downloading {}...".format(book)
        with open(book_path, 'wb') as file:
            response = urlopen(url)
            if response.code == OK:
                file.write(response.read())
        return True
    except Exception as e:
        print e
        return False

def show_status(book_name, status):
    if status:
        print "{} downloaded successfully....\n".format(book_name)
    else:
        print "ERROR: Downloading {} failed\n".format(book_name)

def get_complete_series():
    for book_url, book_name in get_book_details():
        # Escape special characters in url
        safe_url = quote(book_url, safe="%/:.")
        show_status(book_name, download_book(safe_url, book_name))

def get_single_book(name):
    book_name = name + ".pdf"
    url =  URL + book_name
    safe_url = quote(url, safe="%/:.")
    show_status(book_name, download_book(safe_url, book_name))

def show_help():
    print "======== Animorphs Series Downloader ========="
    print "Usage:\n"
    print "python animorphs-downloader.py --all                 Download entire series"
    print "python animorphs-downloader.py --book [book]         Download single book\n\n"
    print "[book]       Books Available\n"
    print "\t\t01 - 54"
    for book in MEGAMORPHS + OTHERS:
        print "\t\t", book


if __name__ == '__main__':
    import sys
    try:
        if sys.argv[1] == "--help":
            show_help()
        elif sys.argv[1] == "--booknumber" and sys.argv[2]:
            get_single_book(sys.argv[2])
        elif sys.argv[1] == "--all":
            get_complete_series()
    except:
        show_help()
