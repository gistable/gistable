#! /usr/bin/python

import os
import re

in_log_path = '/var/log/apache2/clickheat/'
out_log_path = '/var/www/clickheat/logs/'

site_files = []

def outfile(site, group, filename):
    _dir = out_log_path + site + ',' + group
    path = _dir + '/' + filename

    e = False
    for p, fh in site_files:
        if p == path:
            return fh
    if not e:
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        fh = open(path , 'w+')
        site_files.append((path, fh))
        return fh

for filename in os.listdir(in_log_path):
    in_file = open(in_log_path + filename , 'r')

    for line in in_file.readlines():
        # PARSE THIS:
        # GET /clickheat/clickempty.html?s=vb.is&g=all&x=543&y=223&w=1074&b=msie&c=1&random=Wed%20Feb%2016%2016:58:54%202011 HTTP/1.0
        _values = line.split('&')
        values = []

        for v in _values:
            l = v.split('=')
            if len(l) == 2:
                values.append(l[1])

        try:
            (site, group, x, y, w, browser, c) = values[:7]
        except:
           continue


        if site and group:
            line = '|'.join([x,y,w,browser,c]) + "\n"

            outfile(site, group, filename).write(line)

    in_file.close()

    for path, fh in site_files:
        fh.close()