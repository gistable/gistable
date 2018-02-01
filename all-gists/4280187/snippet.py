#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, argparse, textwrap
from argparse import RawTextHelpFormatter

operators = ["AND", "OR"]
arxiv_url = "http://arxiv.org/find/all/1/"
suffix = "/0/1/0/all/0/1"

def main(search_string):
    search_string = " ".join(str(x) for x in search_string)
    search_string = search_string.strip()

    search_string = search_string.replace(' ', '+')
    search_string = search_string.split('+')

    new_string = []
    for term in search_string:
        if term.upper() in operators:
            new_string.insert(0, term.upper())
        else:
            new_string.append(term)

    new_string = "+".join(new_string)
    new_string = new_string.replace(':', ':+')

    url = arxiv_url + new_string + suffix

    launcher = "/usr/bin/x-www-browser"
    os.execv(launcher, [launcher, url])

if __name__ == "__main__":
    overview = "Search arXiv from the command line. Launches results in x-www-browser"

    query_help = ("Boolean arXiv query\n"
                 "Eg. cat:math.CT AND abs:monoidal AND abs:braided\n"
                 "See http://arxiv.org/multi?group=grp_math&find=Search for additional search parameters")

    parser = argparse.ArgumentParser(description=overview, formatter_class=RawTextHelpFormatter)
    parser.add_argument('query', metavar='QUERY', nargs='*', help=query_help)
    pargs = parser.parse_args()

    main(pargs.query)