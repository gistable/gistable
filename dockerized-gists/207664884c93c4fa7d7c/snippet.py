#! /usr/bin/env python
from __future__ import print_function
from HTMLParser import HTMLParser
import argparse
import urlparse
import urllib2

# Brief python script to print out all links found on a web page.
# Useful for 'wget'-ing a bunch of items given in an Apache directory


# Way of extracting all links from a page.
# Originally found here:
#     http://stackoverflow.com/a/3075561
class GetLinksParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.link_list = []
    def get_links(self):
        return self.link_list
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.link_list.append(value)

def expand_link(inurl, link_list):
    """Gets the full canonical url from what might be a relative one"""
    to_ret = []
    for link in link_list:
        to_ret.append(urlparse.urljoin(inurl, link))
    return to_ret

# Gets all the links on a page
def get_all_links(inurl):
    """Gets all the links on a page"""
    parser = GetLinksParser()
    page = urllib2.urlopen(inurl).read()
    parser.feed(page)
    link_list = expand_link(inurl, parser.get_links())
    return link_list

# We really don't want to accidentally open a gigantic file/folder because
# that'd slow us down hugely. So, we only open urls that are less than an
# arbitrary (small) size.
def url_small_enough(link, inurl):
    meta = urllib2.urlopen(link).info()
    head = meta.getheaders('Content-Length')
    if len(head) > 0:
        url_size = int(head[0])
    else:
        return False

    if url_size < 30000: # Arbitrary size
        # Crappy heuristic ensuring only checking child pages
        if len(link) >= len(inurl):
            return True
    else:
        return False


# Why all the "existing links" checks?
#
# We have to make sure we never hit the same link twice because if we did, we
# may very well end up in an infinite loop, or accidentally walk up the tree (by
# following a "parent directory" link). This is especially important in Apache
# open directories, since they tend to have link sturctures that could loop
def recursive_get_links(inurl, existing_links=None, depth=0):
    if existing_links is None:
        existing_links = []
    if inurl not in existing_links:
        existing_links.append(inurl)

    to_ret = []
    link_list = get_all_links(inurl)
    to_ret += link_list
    for link in link_list:
        if depth and (link[-1] == '/') and url_small_enough(link, inurl)\
           and link not in existing_links:
            to_ret += recursive_get_links(link, to_ret+existing_links, depth=depth-1)
    return to_ret

def main():
    parser = argparse.ArgumentParser('Prints links found in the HTML at the given url')
    parser.add_argument('--filter', required=False, default=None,
                        help="Filters for links that contain given string.")
    parser.add_argument('url', help="Url to scrape for links.")
    parser.add_argument('--depth', required=False, type=int, default=0,
                        help="Max depth of links to scrape. Default is '0'.")

    args = parser.parse_args()

    filt = args.filter
    depth = args.depth
    inurl = args.url


    link_list = recursive_get_links(inurl, depth=depth)
    if filt:
        filtered_list = [link for link in link_list if filt in link]
        for link in sorted(list(set(filtered_list))): # Sets remove duplicates
            print(link)
    else:
        for link in sorted(list(set(link_list))):
            print(link)

if __name__ == '__main__':
    main()

