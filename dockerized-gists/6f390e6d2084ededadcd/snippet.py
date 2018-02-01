#!/usr/bin/env python3

import lxml.html
import argparse


class RSS:
    def __init__(self, url):
        assert(url != "")
        self.url = url

        try:
            main = lxml.html.parse(self.url)
            if main.xpath("/html/body/rss"):
                self.title = main.xpath("/html/body/rss/channel/title")[0].text
                self.desc = main.xpath("/html/body/rss/channel/description")[0].text
                self.items = list(zip(
                    [ x.text for x in main.xpath("/html/body/rss/channel/item[*]/title") ],
                    [ x.text for x in main.xpath('/html/body/rss/channel/item[*]/guid') ],
                    [ x.text for x in main.xpath("/html/body/rss/channel/item[*]/description") ]))
            elif main.xpath("/html/body/feed"):
                self.title = main.xpath("/html/body/feed/title")[0].text
                self.desc = main.xpath("/html/body/feed/subtitle")[0].text
                self.items = list(zip(
                    [ x.text for x in main.xpath("/html/body/feed/entry[*]/title") ],
                    [ x.text for x in main.xpath('/html/body/feed/entry[*]/origlink') ],
                    [ x.text for x in main.xpath("/html/body/feed/entry[*]/content") ]))
            else:
                pass

        except:
            print("Something got wrong o_O!")
            raise RuntimeError

    def get_url(self):
        return self.url

    def get_title(self):
        return self.title

    def get_desc(self):
        return self.desc

    def get_items(self):
        return self.items

    def get_nth_item(self, n):
        assert( n < len(self.items))
        return self.items[n]



def __test():
    r = RSS('http://feeds.bbci.co.uk/news/rss.xml')
    r = RSS('http://rss.slashdot.org/Slashdot/slashdot')
    r = RSS('http://www.phoronix.com/rss.php')
    r = RSS('http://www.36kr.com/feed/')
    print(r.get_nth_item(3))

if __name__ == '__main__':
    #__test()

    parser = argparse.ArgumentParser(description='RSS fetcher')
    parser.add_argument('--url', '-u' , required=True, type=str,  help='feed url')
    parser.add_argument('--title', '-t', action='store_true', help='get title of the feed' )
    parser.add_argument('--description', '-d', action='store_true', help='get description of the feed' )
    parser.add_argument('--items', '-i', action='store_true', help='get items of the feed' )
    parser.add_argument('--items_no', '-n', nargs=1, type=int, help='get the #N item of the feed' )
    args = parser.parse_args()
    r = RSS(args.url)

    if args.title:
        print(r.get_title())

    if args.description:
        print(r.get_desc())

    if args.items:
        for i in r.get_items():
            for r in i:
                print(r)

    if args.items_no:
        for r in r.get_nth_item(args.items_no[0]):
            print(r)

