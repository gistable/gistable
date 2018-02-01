# -*- coding: utf-8 -*-

import re
import sys
import locale

from bs4     import BeautifulSoup
from urllib2 import urlopen


def make_url(query, city, radius):
    query = query.replace(' ', '+').lower()
    city  = city.lower()
    return 'http://www.indeed.co.uk/jobs?q=%s&l=%s&radius=%d' % (query, city, radius)


def get_stats(salaries, counts):

    total = float(0)
    num   = 0

    for s,c in zip(salaries,counts):
        total += s * c
        num   += c

    return num, total / num


if __name__  == '__main__':

    locale.setlocale(locale.LC_ALL, 'en_US')

    ## Input parsing
    argc = len(sys.argv)

    if argc < 3:
        raise Exception('Too few arguments')
    elif argc > 4:
        raise Exception('Too many arguments')
    
    city   = sys.argv[1]
    query  = sys.argv[2]
    radius = int(sys.argv[3]) if argc == 4 else 10
    
    ## Fetch the data from indeed.co.uk
    url  = make_url(query, city, radius)
    print '\nReading from %s...\n' % url
    soup = BeautifulSoup(urlopen(url).read())

    ## Pull out the salary summary and process it
    links = soup.find_all('a', title=re.compile('\+ \('))
    salaries, counts = [], []
    salary_regex = '(\d+,000)\+ \((\d+)\)'
    for a in links:
        title = a.get('title').encode('utf-8')
        results = re.search(salary_regex, title).groups()
        salaries.append( int(results[0].replace(',','')) )
        counts.append( int(results[1]) )

    num_jobs, average_salary = get_stats(salaries, counts)

    ## Quick and dirty reporting of results

    print 'Job Title: %s' % query
    print ' Location: %s' % city
    print '   Radius: %d miles' % radius
    print ''
    print ' Salaries:'

    for s,c in zip(salaries, counts):
        print '%8d - %d' % (s,c)

    print ''
    print 'Number of jobs: %s' % locale.format('%d', num_jobs, grouping=True)
    print 'Average salary: £%s' % locale.format('%d', average_salary, grouping=True)


