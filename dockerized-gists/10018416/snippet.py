#! /usr/bin/env python

import argparse as ap
from bs4 import BeautifulSoup
from datetime import datetime
import urllib2

current_time = datetime.now().time()

def format_time(time):
  return "{0:02d}{1:02d}".format(time.hour, time.minute)

def has_no_changes(columns):
  return columns[5] == "0"

def pretty_print(columns):
  return "Departing: {0} - Arriving: {1} - {2}".format(columns[0], columns[3], columns[7].title())

def pretty_print_with_changes(columns):
  return "Departing: {0} [{1} Changes] Arriving: {2} - {3}".format(columns[0], columns[5], columns[3], columns[7].title())

def strip_whitespace(original):
  return ' '.join(original.split())

parser = ap.ArgumentParser(description='Get the next train times between any two stops')

parser.add_argument('-c', '--no-changes', dest='allow_changes', action='store_false', help='only show routes without changes')

parser.add_argument('start')
parser.add_argument('finish')

options = parser.parse_args()

url = "http://ojp.nationalrail.co.uk/service/timesandfares/{0}/{1}/today/{2}/dep".format(options.start, options.finish, format_time(current_time))

req = urllib2.Request(url)
res = urllib2.urlopen(req)
html_doc = res.read()

soup = BeautifulSoup(html_doc)
table = soup.find(id="oft")

for row in table.select(".mtx"):
  columns = [ strip_whitespace(column.text) for column in row.find_all('td') ]
  if has_no_changes(columns):
    print pretty_print(columns)
  elif options.allow_changes:
    print pretty_print_with_changes(columns)
