#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import HTMLParser
import csv
import datetime
import codecs, cStringIO # for UnicodeWriter

response = urllib2.urlopen('http://www.imdb.com/chart/top')
html = response.read()
# the following 2 lines is to fix parse error
html = html.replace('href=http', 'href="http')
html = html.replace('ch_qz', 'ch_qz"')
response.close()

# http://docs.python.org/2/library/csv.html
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class IMDbTop250HTMLParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.in_250_table = False
        self.movie_table = []
        self.movie_entry = []
        self.top250 = []
        self.still_in_data = False
 
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            for (variable, value) in attrs:
                if variable == 'border' and value == '1':
                    self.in_250_table = True
        if tag == 'tr' and self.in_250_table:
            self.movie_entry = []
        if tag == 'a' and self.in_250_table:
            for (variable, value) in attrs:
                if variable == 'href':
                    # fetch imdb movie id from string like "/title/tt0068646/"
                    self.movie_entry.append(value.split('/')[2])

    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_250_table = False
        if tag == 'tr' and self.in_250_table:
            #print self.movie_entry
            self.movie_table.append(self.movie_entry)
        if tag == 'td' or tag == 'a':
            self.still_in_data = False

    def handle_data(self, data):
        if self.in_250_table:
            if self.still_in_data:
                self.movie_entry[-1] = self.movie_entry[-1] + data
                self.still_in_data = False
            else:
                self.movie_entry.append(data)

    def handle_charref(self, name):
        if self.in_250_table:
            char = unichr(int(name[1:], 16))
            self.movie_entry[-1] = self.movie_entry[-1] + char
            self.still_in_data = True
        

    def rearrange(self):
        # after parse, we have the following data
        # ['Rank', 'Rating', 'Title', 'Votes']
        # ['1.', '9.2', 'tt0111161', 'The Shawshank Redemption', ' (1994)', '871,279']
        self.top250.append(['ID', 'Rank', 'Rating', 'Title', 'Year', 'Votes'])
        for e in self.movie_table[1:]:
            #print e
            entry = [e[2], 
                    e[0][:-1], 
                    e[1], 
                    e[3], 
                    e[4][2:-1],
                    e[5].replace(',','')] 
            self.top250.append(entry)

    def save_to_file(self):
        filename = "imdb-top250-%s.csv" % str(datetime.date.today())
        f = open(filename, 'wb')
        f.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
        w = UnicodeWriter(f) #csv.writer(f)
        w.writerows(self.top250)
        f.close()

parser = IMDbTop250HTMLParser()
parser.feed(html)
parser.rearrange()
parser.save_to_file()
parser.close()
