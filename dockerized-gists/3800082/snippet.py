#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    GOOGLE SEARCH
    -------------
    Command line access to advanced Google searches.
    To see all options use the `--help` flag.

    Copyright (c) 2013, T. Zengerink
    Licensed under MIT License
    See: https://gist.github.com/raw/3151357/6806e68cb9cc0042b265f25be9bc25dd39f75267/LICENSE.md
"""

import argparse, os, subprocess, urllib


class GoogleSearch():
    """Build the search string based on the given parameters.
    args -- Arguments as parsed by argparse
    """
    def __init__(self, args):
        self.args = args
        self.search = 'http://google.com/search'

    def __all(self):
        """Get the `match all` part of the query string."""
        if not self.args.all:
            return {}
        return { "as_q" : " ".join(self.args.all) }

    def __any(self):
        """Get the `any` part of the query string."""
        if not self.args.any:
            return {}
        return { "as_oq" : " ".join(self.args.any) }

    def __country(self):
        """Get the `country` part of the query string."""
        if not self.args.country:
            return {}
        return { "cr" : "country" + "".join(self.args.country).upper() }

    def __exact(self):
        """Get the `exact match` part of the query string."""
        if not self.args.exact:
            return {}
        return { "as_epq" : " ".join(self.args.exact) }

    def __in(self):
        """Get the `terms in` part of the query string."""
        if not self.args.appears_in:
            return {}
        return { "as_occt" : "".join(self.args.appears_in) }

    def __language(self):
        """Get the `language` part of the query string."""
        if not self.args.language:
            return {}
        return { "lr" : "lang_" + "".join(self.args.language) }

    def __level(self):
        """Get the `reading level` part of the query string."""
        if not self.args.level:
            return {}
        D = {
            'any' : 'rl:1',
            'b'   : 'rl:1,rls:0',
            'i'   : 'rl:1,rls:1',
            'a'   : 'rl:1,rls:2',
        }
        return { "tbs" : D["".join(self.args.level)] }

    def __safe(self):
        """Get the `safe search` part of the query string."""
        if not self.args.safe:
            return {}
        return { "safe" : "".join(self.args.safe) }

    def __site(self):
        """Get the `site or domain` part of the query string."""
        if not self.args.site:
            return {}
        return { "as_sitesearch" : " ".join(self.args.site) }

    def __type(self):
        """Get the `file type` part of the query string."""
        if not self.args.type:
            return {}
        return { "as_filetype" : "".join(self.args.type) }

    def __query(self):
        """Get the `query` part of the search query string."""
        if not self.args.query:
            return {}
        return { "q" : " ".join(self.args.query) }

    def __range(self):
        """Get the `range` part of the query string."""
        if not self.args.range:
            return {}
        return {
            "as_nlo" : self.args.range[0],
            "as_nhi" : self.args.range[1],
        }

    def __rights(self):
        """Get the `usage rights` part of the query string."""
        if not self.args.rights:
            return {}
        D = {
            "fu" : "(cc_publicdomain|cc_attribute|cc_sharealike|"
                   + "cc_noncommercial|cc_nonderived)",
            "cu" : "(cc_publicdomain|cc_attribute|cc_sharealike|"
                   + "cc_nonderived).-(cc_noncommercial)",
            "fm" : "(cc_publicdomain|cc_attribute|cc_sharealike|"
                   + "cc_noncommercial).-(cc_nonderived)",
            "cu" : "(cc_publicdomain|cc_attribute|"
                   + "cc_sharealike).-(cc_noncommercial|cc_nonderived)",
        }
        return { "as_rights" : D["".join(self.args.rights)] }

    def __update(self):
        """Get the `last update` part of the query string."""
        if not self.args.update:
            return {}
        return { "as_qdr" : "".join(self.args.update) }

    def query_string(self):
        return urllib.urlencode(dict(self.__query().items()
                                     + self.__all().items()
                                     + self.__any().items()
                                     + self.__exact().items()
                                     + self.__range().items()
                                     + self.__language().items()
                                     + self.__country().items()
                                     + self.__update().items()
                                     + self.__site().items()
                                     + self.__safe().items()
                                     + self.__in().items()
                                     + self.__level().items()
                                     + self.__type().items()
                                     + self.__rights().items()))

    def url(self):
        """Get the URL to request from the browser."""
        qs = self.query_string()
        return self.search + ('?' + qs if qs else '')


def handle_args():
    """Handle the passed arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('query',
                        default='',
                        help='Search terms',
                        nargs='*')
    parser.add_argument('-a', '--all',
                        default='',
                        dest='all',
                        help='All these words',
                        nargs='+')
    parser.add_argument('-A', '--any',
                        default='',
                        dest='any',
                        help='Any of these words',
                        nargs='+')
    parser.add_argument('-c', '--country',
                        default='',
                        dest='country',
                        help='Country (ISO 3166-1 code)',
                        nargs=1)
    parser.add_argument('-e', '--exact',
                        default='',
                        dest='exact',
                        help='Exact word or phrase',
                        nargs='+')
    parser.add_argument('-i', '--in',
                        choices=['any','title','body','url','links'],
                        default='',
                        dest='appears_in',
                        help='Terms appearing in',
                        nargs=1)
    parser.add_argument('-l', '--language',
                        default='',
                        dest='language',
                        help='Language (ISO 639-1 code)',
                        nargs=1)
    parser.add_argument('-L', '--level',
                        choices=['any','b','i','a'],
                        default='',
                        dest='level',
                        help='Reading level (b=Basic, i=Intermediate, '
                             + 'a=Advanced)',
                        nargs=1)
    parser.add_argument('-o', '--output',
                        action='store_true',
                        default=False,
                        dest='output',
                        help='Print the URL instead of trying to open it')
    parser.add_argument('-r', '--range',
                        default='',
                        dest='range',
                        help='numbers ranging from .. to ..',
                        nargs=2)
    parser.add_argument('-R', '--rights',
                        choices=['fu','cu','fm','cm'],
                        default='',
                        dest='rights',
                        help='Usage rights (fu = Free to use, cu = Free to '
                             + 'use, even commercially, fm = Free to use, '
                             + 'share or modify, cm = Free to use, share or '
                             + 'modify, even commercially)',
                        nargs=1)
    parser.add_argument('-s', '--site',
                        default='',
                        dest='site',
                        help='Site or domain',
                        nargs='+')
    parser.add_argument('-S', '--safe',
                        choices=['off','images','active'],
                        default='',
                        dest='safe',
                        help='Safe search',
                        nargs=1)
    parser.add_argument('-t', '--type',
                        choices=['pdf','ps','dwf','kml','kmz','xls','ppt','doc',
                                 'rtf','swf'],
                        default='',
                        dest='type',
                        help='File type',
                        nargs=1)
    parser.add_argument('-u', '--update',
                        choices=['all','h','d','w','y'],
                        default='',
                        dest='update',
                        help='Last update (h = Hour, d = Day, w = Week, '
                             + 'y = Year)',
                        nargs=1)
    return parser.parse_args()


def main():
    args = handle_args()
    gs = GoogleSearch(args)
    if not args.output:
        subprocess.call([os.environ['BROWSER'], gs.url()])
    else:
        print(gs.url())

if __name__ == '__main__':
    main()