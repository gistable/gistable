#!/usr/bin/python
# -*- coding: utf-8 -*-

# Done under Visual Studio 2010 using the excelent Python Tools for Visual Studio
# http://pytools.codeplex.com/
#
# Article on ideas vs execution at: http://blog.databigbang.com/ideas-and-execution-magic-chart/

import urllib2
import json
from datetime import datetime
from time import mktime
import csv
import codecs
import cStringIO

class CSVUnicodeWriter: # http://docs.python.org/library/csv.html
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

def get_hackernews_articles_with_idea_in_the_title():
    endpoint = 'http://api.thriftdb.com/api.hnsearch.com/items/_search?filter[fields][title]=idea&start={0}&limit={1}&sortby=map(ms(create_ts),{2},{3},4294967295000)%20asc'

    incomplete_iso_8601_format = '%Y-%m-%dT%H:%M:%SZ'

    items = {}
    start = 0
    limit = 100
    begin_range = 0
    end_range = 0

    url = endpoint.format(start, limit, begin_range, str(int(end_range)))
    response = urllib2.urlopen(url).read()
    data = json.loads(response)

    prev_timestamp = datetime.fromtimestamp(0)

    results = data['results']

    while results:
        for e in data['results']:
            _id = e['item']['id']
            title = e['item']['title']
            points = e['item']['points']
            num_comments = e['item']['num_comments']
            timestamp = datetime.strptime(e['item']['create_ts'], incomplete_iso_8601_format)

            #if timestamp < prev_timestamp: # The results are not correctly sorted. We can't rely on this one.             if _id in items: # If the circle is complete.                 return items             prev_timestamp = timestamp                      items[_id] = {'id':_id, 'title':title, 'points':points, 'num_comments':num_comments, 'timestamp':timestamp}             title_utf8 = title.encode('utf-8')             print title_utf8, timestamp, _id, points, num_comments         start += len(results)         if start + limit > 1000:
            start = 0
            end_range = mktime(timestamp.timetuple())*1000

        url = endpoint.format(start, limit, begin_range, str(int(end_range))) # if not str(int(x)) then a float gives in the sci math form: '1.24267528e+12'
        response = urllib2.urlopen(url).read()
        data = json.loads(response)
        results = data['results']

    return items

if __name__ == '__main__':
    items = get_hackernews_articles_with_idea_in_the_title()

    with open('hn-articles.csv', 'wb') as f:
        hn_articles = CSVUnicodeWriter(f)

        hn_articles.writerow(['ID', 'Timestamp', 'Title', 'Points', '# Comments'])

        for k,e in items.items():
            hn_articles.writerow([str(e['id']), str(e['timestamp']), e['title'], str(e['points']), str(e['num_comments'])])

# It returns 3706 articles where the query says that they are 3711... find the bug...