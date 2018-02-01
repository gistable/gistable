"""python -m pipwin pycuda-2016.1.2+cuda7518-cp34-cp34m-win_amd64.whl"""

from __future__ import absolute_import, division, print_function

import argparse
import os
import shutil
import tempfile
import sys

from six import print_ as print
from six.moves import html_parser, urllib


class Parser(html_parser.HTMLParser):

    package = None
    route = None

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        for key, href in attrs:
            if key == 'href' and href == 'javascript:;':
                break
        else:
            return
        for key, onclick in attrs:
            if key == 'onclick':
                break
        else:
            return
        ml = [int(i) for i in onclick.split('"')[0].split('(')[1].strip()[1:-2].split(',')]
        mi = onclick.split('"')[1].replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        route = ''.join(chr(ml[ord(i) - 47]) for i in mi)
        if self.package in route:
            self.route = route


def download_wheel_gohlke(package, directory=None):
    url = 'http://www.lfd.uci.edu/~gohlke/pythonlibs/'
    if sys.version_info.major < 3:
        parser = Parser()
    else:
        parser = Parser(convert_charrefs=True)
    parser.package = package
    request = urllib.request.Request(url, headers={'User-Agent': '...'})
    response = urllib.request.urlopen(request)
    if sys.version_info.major < 3:
        source = response.read()
    else:
        source = response.read().decode()
    response.close()
    line42 = (
        """if (top.location!=location) top.location.href=location.href;"""
        """function dc(ml,mi){var ot="";for(var j=0;j<mi.length;j++)ot+=String.fromCharCode(ml[mi.charCodeAt(j)-47]);document.write(ot);}"""
        """function dl1(ml,mi){var ot="";for(var j=0;j<mi.length;j++)ot+=String.fromCharCode(ml[mi.charCodeAt(j)-47]);location.href=ot;}"""
        """function dl(ml,mi){mi=mi.replace('&lt;','<');mi=mi.replace('&#62;','>');mi=mi.replace('&#38;','&');setTimeout(function(){dl1(ml,mi)},1500);}""")
    assert line42 in source, '"{}" source was changed'.format(url)
    parser.feed(source)
    assert parser.route is not None, 'Failed to find "{}"'.format(package)
    url += parser.route
    if directory is None:
        directory = tempfile.gettempdir()
    path = os.path.join(directory, os.path.basename(url))
    request = urllib.request.Request(url, headers={'User-Agent': '...'})
    response = urllib.request.urlopen(request)
    with open(path, 'wb') as f:
        shutil.copyfileobj(response, f)
    response.close()
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('packages', nargs='+', help='')
    parser.add_argument('-d', '--directory', help='')
    args = parser.parse_args()
    for package in args.packages:
        print(download_wheel_gohlke(package, args.directory))
