#!/usr/bin/env python2
# coding: utf-8
from __future__ import print_function
import sys
import re
import json
import urllib
from colorama import init, Fore, Back, Style

URL = 'http://csearch.naver.com/dcontent/spellchecker.nhn'

def get(url):
    return urllib.urlopen(url).read()

def main(q):
    response = get(URL + '?_callback=window.__jindo2_callback._spellingCheck_0&q=' + urllib.quote(q.encode('utf8')))
    matched = re.search(r'.*?\((.*)\);', response)
    if matched:
        obj = json.loads(matched.group(1))
        result = obj['message']['result']
        print('errata_count : {}'.format(result['errata_count']))
        html = result['html']
        html = re.sub(r"<span class='re_red'>", Fore.RED, html)
        html = re.sub(r"<span class='re_green'>", Fore.GREEN, html)
        html = re.sub(r"<span class='re_purple'>", Fore.MAGENTA, html)
        html = re.sub(r'<\/?.*?>', Style.RESET_ALL, html)
        init()
        print('before : ' + q)
        print('after  : ' + html)
        print('')
        print('HELP : ', end='')
        print(Fore.RED + u'맞춤법', end=' ')
        print(Fore.GREEN + u'띄어쓰기', end=' ')
        print(Fore.MAGENTA + u'표준어 의심단어')
        print(Style.RESET_ALL)
    else:
        print('no result.')

if __name__ == '__main__':
    try:
        q = sys.argv[1].decode('utf8')
    except IndexError:
        sys.exit(1)

    main(q)
