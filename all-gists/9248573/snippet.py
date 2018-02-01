#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq

def main():
    # 気象庁 東京 2014年1月データ
    url = ('http://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?'
           'prec_no=44&block_no=47662&year=2014&month=1&day=&view=')
    #  pyquery
    query = pq(url, parser='html')
    # title の取得
    title = query('title').text()
    # 日毎を取得
    day = query('.data_0_0')

    print title
    for i, item in enumerate(day):
        if i % 20 == 5:
            print('{:02d}日の平均気温 {} ℃'
                  .format(i / 20 + 1, pq(item).text()))

if __name__ == '__main__':
    main()
