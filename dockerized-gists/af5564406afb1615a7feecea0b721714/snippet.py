#!/usr/bin/env python3
#(works for 2.7 as well)
#todo: add support for <script>window.location='nsa.gov'<script>
import requests
import sys
def get_loc(url):
    try:
        h=requests.head(url).headers['location']
        return h
    except KeyError:
        return 'END'


urlcnt=len(sys.argv)-1

if urlcnt == 0:
    print('please enter in a url')
    sys.exit(1)

headloop = get_loc(sys.argv[1])
while headloop != 'END':
    print(headloop)
    headloop = get_loc(headloop)