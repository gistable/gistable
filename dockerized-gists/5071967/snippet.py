# -*- coding: utf-8

from bs4 import BeautifulSoup
import requests
import re


def scrape_index_page():
    """
    Returns a list of URLs to scrape.
    """
    url_list = []
    domain_root = 'http://www.iardc.org'
    url = u'%s/co_recentdiscdec.html' % domain_root

    request = requests.get(url)
    html = request.content

    parsed_html = BeautifulSoup(html)

    for link in parsed_html.select('body > div table')[1].findAll('a')[56:90]:
        detail_url = '%s/%s' % (domain_root, link['href'])
        if u'recentdiscdec_' in detail_url:
            detail_request = requests.get(detail_url)
            url_list.append((detail_request.content, url))

    return url_list


def standard_format(case_text):
    return int(
        case_text.split('-')[0]\
        .replace('M.R.', '')\
        .strip())


def regex_format(case_text):
    regex = re.compile(r'(M.R.\s\d+)')
    result = regex.search(case_text)
    return int(
        result.groups()[0]\
        .replace('M.R. ', '')\
        .strip())


def emdash_format(case_text):
    return int(
        case_text\
        .split(u'‑')[0]\
        .strip()\
        .replace('M.R.', '')\
        .strip())

def scrape_detail_page(html, url):
    """
    Scrapes detail pages.
    Requires html and the URL of the page the HTML originates from.
    """
    lawyer_dict = {}
    parsed_html = BeautifulSoup(html)
    try:
        cases = parsed_html.select('body > div table')[1].findAll('p')
        for case in cases:
            if u'M.R.' in case.text.strip():
                case_text = case.text\
                    .strip()\
                    .replace('\n', '')\
                    .replace('\r', '')\
                    .replace('  ', '')\
                    .replace('\t', '')\
                    .replace('\f', '')

                # M.R.21877 - In re: Larry E. Smith. (March 17, 2008)
                




    except IndexError:
        print 'URK!'

    # print lawyer_dict

# Set up a list of URLs to scrape.
url_list = scrape_index_page()

# Check that we have at least one.
if len(url_list) > 0:

    # Loop through the list.
    for html, url in url_list:

        # Scrape the page.
        scrape_detail_page(html, url)
