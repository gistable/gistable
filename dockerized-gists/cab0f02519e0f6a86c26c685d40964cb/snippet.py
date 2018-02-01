# -*- coding: utf-8 -*-

import os
import sys
import grequests
import numpy as np
import pandas as pd
from lxml import html
from time import sleep
from datetime import date, timedelta

def scrape():
    URI = 'http://text.npr.org/p.php?pid=3&d={}'
    HEADERS_DEFAULT = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    
    dates = []
    
    d1 = date(2002, 10, 29)  # start date
    d2 = date(2017, 10, 28)  # end date

    delta = d2 - d1          # timedelta
    
    for i in range(delta.days + 1):
        date_string = str(d1 + timedelta(days=i)).replace('-', '')
        dates.append(date_string)
    
    responses = []
    
    for dts in np.array_split(dates, 20):
        dts = list(dts)
        responses += grequests.map(grequests.get(URI.format(dt), headers=HEADERS_DEFAULT) for dt in dts)
        sleep(5)
    
    results = []
    
    failed = 0
    for (dt, rs) in zip(dates, responses):
        if rs:
            rs = html.fromstring(rs.content)
            list_of_articles = rs.xpath('/html/body/ul[1]').pop()
            for article in list_of_articles.iterchildren():
                if article.text:
                    label = article.text.strip().replace(':', '')
                    title = article.xpath('a/text()').pop()
                    results.append((dt, label, title))
        else:
            failed += 1
    
    print 'No data for', failed, 'days'
            
    df = pd.DataFrame(results, columns=['date', 'label', 'title'])
    df.to_csv('scraped_data.csv', index=False, encoding='utf-8')

if __name__ == '__main__':
    scrape()