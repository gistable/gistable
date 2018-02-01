#!/usr/bin/env python3
# coding: utf8
# GistID: 8232376

import optparse
import sys
from subprocess import check_call
from urllib.parse import urlparse, quote, urlencode


def parseargs(argv=sys.argv):
    parser = optparse.OptionParser()
    parser.add_option('-g', '--genre', help="Genre", dest='genre')
    return parser.parse_args(argv)


def soundcloud_uri(query, options=None, mode='search'):
    options = options or {}
    options = {k: v for k, v in options.items() if v}
    url = "soundcloud://{}/{}?{}"
    return url.format(mode, quote(query), urlencode(options))



def main():
    cmd = ['mpc', 'load']
    MODES = set(("search", "user", "tracks", "url", "playlist"))

    argv = list(sys.argv)[1:]
    if argv[0] in MODES:
        mode = argv.pop(0)
    else:
        mode = 'search'
    opt, args = parseargs(argv)
    query = ' '.join(args)
    url = soundcloud_uri(query, vars(opt), mode)
    cmd.append(url)
    print(cmd)
    check_call(cmd)

if __name__ == '__main__':
    main()