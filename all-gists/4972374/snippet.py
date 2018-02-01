#!/usr/bin/env python

import os
import yaml
import datetime
from collections import OrderedDict

__doc__ = 'A quick script for converting octopress posts (markdown source files) to pelican posts'


# configure following variables according to your blog
blog_author = 'Vineet Naik'

# a sorted order of metadata for consistency
metadata_order = ['Title', 'Author', 'Date', 'Tags', 'Category', 'Summary']


def octopress_files(path):
    def is_md(f):
        return os.path.splitext(f)[1] in ('.md', '.markdown')
    return (os.path.join(path, f) for f in os.listdir(path) if is_md(f))


def parse(lines):
    """Parses lines of an octopress markdown file and returns an un-named
    tuple of metadata dict and body of the post in that order

    """
    in_yaml = False
    metadata = []
    body = []
    for line in lines:
        if line == '---' and not in_yaml:
            in_yaml = True
        elif line == '---' and in_yaml:
            in_yaml = False
        elif in_yaml:
            metadata.append(line)
        else:
            body.append(line)
    return (yaml.load('\n'.join(metadata)), '\n'.join(body))


def pelicanize(filepath):
    """Takes a path to octopress post file and `pelicanizes` it. Returns
    an un-named tuple of the pelican post filename and the post in
    that order

    """
    with open(filepath) as f:
        lines = (line.rstrip('\n') for line in f)
        yml, content = parse(lines)
        metadata = pelicanize_metadata(yml)
        body = pelicanize_body(content)
        content = ''
        for k, v in metadata.iteritems():
            content += '%s: %s\n' % (k, v)
        content += '\n'
        content += body
    filename = pelicanize_filename(os.path.basename(filepath))
    return (filename, content)


def pelicanize_filename(filename):
    """Gets rid of date portion in the octopress filenames"""
    name, ext = os.path.splitext(filename)
    return '%s.md' % ('-'.join(name.split('-')[3:]),)


def pelicanize_metadata(metadata):
    """Converts the octopress style metadata (yaml in md files) to pelican
    style metadata.

    Basically, removes unnecessary data, capitalizes the keys and
    sorts in a standard order (not a pelican requirement, but rather
    to maintain consistency)

    """
    not_required = ('layout', 'link', 'published', 'comments')
    metadata = dict([(k, ', '.join(v) if type(v)==list else v)
                     for k, v in metadata.iteritems()
                     if k not in not_required])
    metadata['date'] = str(metadata['date'])
    metadata['Summary'] = ''
    metadata['Author'] = blog_author
    if 'categories' in metadata:
        metadata['Category'] = metadata['categories']
        del metadata['categories']
    meta = dict(zip(map(str.capitalize, metadata.keys()), metadata.values()))

    return OrderedDict(sorted(meta.items(), 
                              cmp=lambda x, y: cmp(metadata_order.index(x[0]),
                                                   metadata_order.index(y[0]))))


def pelicanize_body(body):
    return body


def test():
    orig = '2012-05-04-own-the-editor.markdown'
    assert pelicanize_filename(orig) == 'own-the-editor.md'

    octo_meta = {'categories': ['jquery', 'javascript'],
                 'comments': True,
                 'date': datetime.datetime(2009, 8, 23, 23, 47, 23),
                 'layout': 'post',
                 'link': 'http://vineetnaik.me/blog/2009/08/a-self-made-jquery-slider/',
                 'published': True,
                 'tags': ['jquery',
                          'slider',
                          'image gallery'],
                 'title': 'A self made Jquery slider'}
    pelican_meta = pelicanize_metadata(octo_meta)
    for k in ('comments', 'layout', 'link', 'published'):
        assert not k in pelican_meta

    assert pelican_meta['Category'] == 'jquery, javascript'
    assert pelican_meta['Tags'] == 'jquery, slider, image gallery'
    assert pelican_meta['Title'] == 'A self made Jquery slider'
    assert pelican_meta['Date'] == '2009-08-23 23:47:23'
    assert pelican_meta['Author'] == blog_author
    
    print 'All tests pass.'    


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--source', required=True, help='Source dir or path to the octopress source files')
    parser.add_argument('-t', '--target', required=True, help='Target dir or path to the output directory')
    args = parser.parse_args()

    source_files = octopress_files(args.source)
    pelican_posts = (pelicanize(x) for x in source_files)
    for (filename, post) in pelican_posts:
        print filename
        with open(os.path.join(args.target, filename), 'w') as f:
            f.write(post)
    
