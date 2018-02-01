#!/usr/bin/python

import os
import sys
import argparse
import iso8601
import re
import subprocess
import logging
import json

import requests
from lxml import etree
from lxml.cssselect import CSSSelector
from HTMLParser import HTMLParser

namespaces = {
    'atom': 'http://www.w3.org/2005/Atom',
    'app': 'http://purl.org/atom/app#',
    }
kind_post = 'http://schemas.google.com/blogger/2008/kind#post'
markdown_api = 'http://fuckyeahmarkdown.com/go/'

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--online', '--fuckyeah',
            action='store_const', const='online', dest='converter')
    p.add_argument('--pandoc',
            action='store_const', const='pandoc', dest='converter')
    p.add_argument('--html2text',
            action='store_const', const='html2text', dest='converter')
    p.add_argument('--output-dir', '-d', default='posts')
    p.add_argument('input')
    p.set_defaults(converter='pandoc')
    return p.parse_args()

def markdownify_html2text(html):
    p = subprocess.Popen(['html2text', '-d', '-b', '0', ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    stdout, stderr = p.communicate(input=html.encode('utf-8'))

    return stdout

def markdownify_pandoc(html):
    p = subprocess.Popen(['pandoc', '--strict', '--normalize',
        '-f', 'html', '-t', 'markdown', '-'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    stdout, stderr = p.communicate(input=html.encode('utf-8'))

    return stdout

def markdownify_online(html):
    r = requests.post(markdown_api,
            data=dict(html=html))
    return r.content

def process_entry(entry):
    kind = entry.xpath(
            'atom:category[@scheme="http://schemas.google.com/g/2005#kind"]',
            namespaces=namespaces)[0]
    if kind.get('term') != kind_post:
        return

    eid = entry.xpath('atom:id',
            namespaces=namespaces)[0].text

    title = entry.xpath('atom:title[@type="text"]',
            namespaces=namespaces)[0]
    title = title.text.strip().replace('\n', ' ')
    title = re.sub(' +', ' ', title)

    published = entry.xpath('atom:published', namespaces=namespaces)[0].text
    published = iso8601.parse_date(published)
    published = '%s-%s-%s' % (
            published.year,
            published.month,
            published.day)

    tags = entry.xpath(
            'atom:category[@scheme="http://www.blogger.com/atom/ns#"]',
            namespaces=namespaces)
    tags = [ x.get('term') for x in tags ]

    try:
        href = entry.xpath('atom:link[@rel="alternate" and @type="text/html"]',
                namespaces=namespaces)[0].get('href')
    except IndexError:
        logging.error('no link for id %s' % eid)
        return

    slug = href.split('/')[-1].replace('.html', '')

    content = entry.xpath('atom:content',
            namespaces=namespaces)[0].text

    return dict(
            id=eid,
            title=title,
            date=published,
            tags=tags,
            href=href,
            content=content,
            slug=slug,
            )

def update_content(entry):
    '''Blogger performs some odd transformations on <pre> blocks when
    producing the Atom feed.  Here we replace the content from the XML file
    by fetching it directly from the <link> specified for the entry.'''
    logging.info('Updating content from %(href)s' % entry)
    r = requests.get(entry['href'])
    doc = etree.fromstring(r.content,
            parser = etree.HTMLParser())
    content = CSSSelector('div.entry-content')(doc)[0]
    entry['content'] = etree.tostring(content)

def write_entry(entry, data, opts):
    # Write xml data to posts/slug.xml.
    with open(os.path.join(opts.output_dir, '%s.xml' % data['slug']), 'w') as fd:
        fd.write(etree.tostring(entry))

    # Write HTML content to posts/slug.html
    with open(os.path.join(opts.output_dir, '%s.html' % data['slug']), 'w') as fd:
        fd.write(data['content'].encode('utf-8'))

    if opts.converter == 'online':
        mdfunc = markdownify_online
    elif opts.converter == 'pandoc':
        mdfunc = markdownify_pandoc
    elif opts.converter == 'html2text':
        mdfunc = markdownify_html2text
    else:
        raise ValueError('Unknown converter (%s)' % opts.converter)

    # Write Markdown to posts/slug.md
    md = mdfunc(data['content'].encode('utf-8'))
    with open(os.path.join(opts.output_dir, '%s.md' % data['slug']), 'w') as fd:
        fd.write('Title: %(title)s\n' % data)
        fd.write('Date: %(date)s\n' % data)
        fd.write('Tags: %s\n' % ' '.join(data['tags']))
        fd.write('\n')
        fd.write(md)

def main():
    opts = parse_args()

    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

    with open(opts.input) as fd:
        logging.info('parsing feed')
        doc = etree.parse(fd)

    for entry in doc.xpath('//atom:entry', namespaces=namespaces):
        data = process_entry(entry)
        if data is None:
            continue

        update_content(data)
        write_entry(entry, data, opts)

if __name__ == '__main__':
    main()

