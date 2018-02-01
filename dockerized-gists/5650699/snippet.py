#!/usr/bin/env python
"""
Downloads and cleans up a CSV file from a Google Trends query.

Usage:
    trends.py google.username@gmail.com google.password /path/to/filename query1 [query2 ...]

Requires mechanize:
    pip install mechanize
"""
import cookielib
import csv
import mechanize
import re
from StringIO import StringIO
import sys

def main(argv):
    # Google Login credentials
    username = argv[1]
    password = argv[2]
    
    # Where to save the CSV file
    pathname = argv[3]

    queries = ('q=' + query for query in argv[4:])

    br = mechanize.Browser()

    # Create cookie jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Act like we're a real browser
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # Login in to Google
    response = br.open('https://accounts.google.com/ServiceLogin?hl=en&continue=https://www.google.com/')
    forms = mechanize.ParseResponse(response)
    form = forms[0]
    form['Email'] = username
    form['Passwd'] = password
    response = br.open(form.click())

    # Get CSV from Google Trends
    trends_url = 'http://www.google.com/trends/trendsReport?'
    query_params = '&'.join(queries)
    response = br.open(trends_url + query_params + '&export=1')

    # Remove headers and footers from Google's CSV
    # Use last date in date range
    reader = csv.reader(StringIO(response.read()))
    dates = []
    values = []
    for row in reader:
        try:
            date, value = row
        except ValueError:
            continue
        if re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}', date):
            dates.append(date[-10:]) # Uses last date in time period
            values.append(value)

    with open(pathname, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'debt'])
        for row in zip(dates, values):
            writer.writerow(row)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
