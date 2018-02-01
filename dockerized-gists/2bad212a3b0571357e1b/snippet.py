import argparse
import hashlib
import os
from collections import defaultdict

import sys
from bs4 import BeautifulSoup as bs
import re
import requests


MD5 = r"^[a-fA-F\d]{32}$"


#
# Finds dependencies of a ubuntu package and downloads all
# needed packages. This might download more than needed
# since some packages can already be installed.
#
# However you can use 'dpkg -i -E *' to install them all
# while skipping already installed packages.
#
class UbuntuDeps(object):

    def __init__(self, arch, release, mirror, fallback):
        self.arch = arch
        self.url = 'http://packages.ubuntu.com/' + release + "/"
        self.mirror = mirror
        self.fallback = fallback

    @staticmethod
    def download_file(_url, _dir):
        local_filename = os.path.join(_dir, _url.split('/')[-1])
        if not os.path.exists(local_filename):
            if not os.path.exists(_dir):
                os.mkdir(_dir)
            r = requests.get(_url, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        return local_filename

    @staticmethod
    def md5(fname):
        _hash = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                _hash.update(chunk)
        return _hash.hexdigest()

    @staticmethod
    def verify_md5(expected, _dep):
        if expected != deps[_dep]['md5']:
            raise ValueError("MD5 check for " + _dep + " failed")

    def find_dep(self, _dep, lvl=0, _deps=None):
        if _deps is None:
            _deps = defaultdict(lambda: defaultdict(dict))
        if _dep in _deps:
            return
        print("*" * lvl + _dep)
        r = requests.get(self.url + _dep)
        soup = bs(r.text, 'html.parser')
        for p in soup.select('p'):
            if any(s in p.text for s in ["No such package", "Package not available in this suite"]):
                print("\nERROR: Could not find package with name " + _dep + " Aborting!")
                sys.exit(1)
            if "This is a virtual package" in p.text:
                prov = soup.select('div#pdeps dl dt a')
                if prov:
                    print("*" * lvl + _dep + " -> " + prov[0].text)
                    _deps[_dep]['url'] = 'REDIR'  # Mark as redirected
                    return self.find_dep(prov[0].text, lvl)
                else:
                    print("\nERROR: Virtual package but could not parse providers. Aborting!")

        # Find the dependencies
        for dl in soup.select('ul.uldep dl'):
            dt = dl.select('dt')[0]
            a = dt.select('a')[0]
            pkg = a.string
            # noinspection PyStatementEffect
            _deps[_dep]
            self.find_dep(pkg, lvl + 1, _deps)

        # Load download page
        r = requests.get(self.url + self.arch + "/" + _dep + "/download")
        soup = bs(r.text, 'html.parser')
        for td in soup.select('table#pdownloadmeta td'):
            if re.match(MD5, td.string):
                _deps[_dep]['md5'] = td.string
        # Find download link
        found = False
        for a in soup.findAll('a'):
            if self.mirror in a['href']:
                _deps[_dep]['url'] = a['href']
                found = True
                break
        if not found:
            for a in soup.findAll('a'):
                if self.fallback in a['href']:
                    _deps[_dep]['url'] = a['href']
                    break
        return _deps

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download ubuntu dependencies',
                                     formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter
                                     (prog=sys.argv[0], max_help_position=80, width=120))
    parser.add_argument('dep', help="The main/top package", nargs='+')
    parser.add_argument('-a', '--arch', help="The architecture to use", default="amd64")
    parser.add_argument('-r', '--release', help="Ubuntu release", default="trusty")
    parser.add_argument('-m', '--mirror', help="Mirror to use for download", default="http://no.archive.ubuntu.com/")
    parser.add_argument('-f', '--fallback', help="Mirror to use when main mirror is not found",
                        default="http://security.ubuntu.com/")
    parser.add_argument('-d', '--directory', help="Target directory", default='pkg')
    args = parser.parse_args()

    ud = UbuntuDeps(arch=args.arch, release=args.release, mirror=args.mirror, fallback=args.fallback)

    deps = None
    for dep in args.dep:
        print("\nDependency tree for " + dep + ":\n")
        deps = ud.find_dep(dep, _deps=deps)

    print("\nNeed to download:")
    for dep in deps.keys():
        print(dep + " : " + str(deps[dep]['url']))

    print()
    for dep in deps.keys():
        if deps[dep]['url'] == 'REDIR':
            continue
        print("Downloading: " + dep)
        ud.verify_md5(ud.md5(ud.download_file(deps[dep]['url'], args.directory)), dep)

