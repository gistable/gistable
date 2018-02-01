#! /usr/bin/env python

#support either python 2 and 3
from __future__ import print_function

import argparse
import os
import sys
import csv

# required extra package
try:
    import requests
except ImportError:
    print('Missing required package "requests".')
    print('Install using "pip install requests" or another method.')
    print('Exiting...')
    sys.exit(1)

# individual files:
# wget --user=dwhite8 --ask-password --output-document=3810068.jpg
# https://www.intra.valpo.edu/bb_pics/pics/auto/pics.php/3828961

HELP = """
Requires: requests package (e.g. "pip install requests")
Usage:

export BB_USER=user
export BB_PASS=pass

%s "Title Name.csv"

Accepts a CSV file exported from Blackboard, which at least contains
the columns "First Name", "Last Name", and "Student ID".  It then
downloads the ID photos of those students and generates a LaTeX document
of the same name with the names and pics in an array.

The script output and all files are in a sub-folder named after the input
CSV file, leaving the .tex file in

"Title Name/Title Name.tex"

A full command line could be:

$ BB_USER=user BB_PASS=pass name="ECE 599" \\
    python make-photo-roster.py "$name.csv" \\
    && cd "$name" && pdflatex "$name.tex"
"""


parser = argparse.ArgumentParser(description="""Create a photo roster.

Blackboard username and password uses the values of environment variables
  BB_USER and BB_PASS if not specified as options.
""")

parser.add_argument('--user', help='Blackboard user name')
parser.add_argument('--pass', dest='password', help='Blackboard password')

orient = parser.add_mutually_exclusive_group()
orient.add_argument('--landscape',
                    help='Output in landscape orientation (default)',
                    action='store_const',
                    const=True,
                    default=True)
orient.add_argument('--portrait',
                    help='Output in portrait orientation',
                    dest='landscape',
                    action='store_const',
                    const=False)

parser.add_argument('--columns',
                    help='Number of columns',
                    metavar='N',
                    type=int)

parser.add_argument('--title',
                    help='Title of sheet, default is CSV basename')

parser.add_argument('csv_file',
                    help='Name of CSV file from Blackboard gradebook export')

opts = parser.parse_args()


LANDSCAPE = opts.landscape

# nice defaults to fill the page
if opts.columns:
    N_COLUMNS = opts.columns
else:
    if LANDSCAPE:
        N_COLUMNS = 6
    else:
        N_COLUMNS = 5

if sys.version_info[0] < 3:
    csvfile = open(opts.csv_file, 'rU')
else:
    csvfile = open(opts.csv_file, 'r', newline='', encoding='iso8859-1')

# except:
    # parser.print_help()
    # sys.exit(1)


if opts.title:
    TITLE = opts.title
else:
    TITLE = opts.csv_file[:-4]


if opts.user:
    BB_USER = opts.user
else:
    BB_USER = os.environ['BB_USER']


if opts.password:
    BB_PASS = opts.password
else:
    BB_PASS = os.environ['BB_PASS']



FOLDER = opts.csv_file[:-4]

JPGNAME_FMT = '{Last Name}_{First Name}_{Student ID}.jpg'

if LANDSCAPE:
    w = 10.0 # = paper_width - 2*margin
    ORIENTATION = 'landscape'
else:
    w = 7.5 # = paper_width - 2*margin
    ORIENTATION = 'portrait'

# always fill max horizontally
IMG_WIDTH = '%fin' % (w / N_COLUMNS)



doc = r"""
\documentclass[letterpaper,%s]{article}
\usepackage{graphicx}
\usepackage{fancyhdr}
\usepackage{longtable}
\usepackage[margin=0.5in]{geometry}
\usepackage{tikz}

\setlength{\topmargin}{-0.5in}

\pagestyle{fancy}
\fancyhf{}
\lhead{\huge \bf %s}
\renewcommand{\headrulewidth}{0pt}

\begin{document}
%%s

\end{document}
""" % (ORIENTATION, TITLE)



table = r"""
\renewcommand{\arraystretch}{0.0}
\setlength{\tabcolsep}{0em}

\begin{longtable}{%s}
%%s
\end{longtable}
""" % (N_COLUMNS * 'l')



element = r"""
\begin{{tikzpicture}}
\node[inner sep=0pt] (a) at (0,0) {{\includegraphics[width=%s]{{{filename}}}}};
\node[preaction={{fill=black, fill opacity=0.3}},
      anchor=south west,
      inner sep=2pt,
      rounded corners=0ex,
      font=\fontfamily{{phv}}\color{{white}},
      align=left,
      text width=%s - 4pt]
        (b) at (a.south west) {{ \LARGE {first} \\ \Large {last} }};
\end{{tikzpicture}}
""" %(IMG_WIDTH, IMG_WIDTH)



picUrl = 'https://www.intra.valpo.edu/bb_pics/pics/auto/pics.php/%s'


# the first 3 bytes of Blackboard CSV files are a
# UTF-8 byte-order-mark "0xEF BB BF"
# HACK: just throw them out!
csvfile.read(3)

reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')


if not os.path.exists(FOLDER):
    os.mkdir(FOLDER)


s = ''
n = 0
for row in reader:
    last = row['Last Name']
    first = row['First Name']
    sid = row['Student ID']


    jpgname = JPGNAME_FMT.format(**row)
    savename = FOLDER + '/' + jpgname
    if not os.path.exists(savename):
        url = picUrl % sid
        r = requests.get(url, auth=(BB_USER, BB_PASS))
        if r.status_code != 200:
            print('URL: %s' % url)
            raise("Something went wrong retrieving the image")
        open(savename, 'wb').write(r.content)

    s += element.format(filename=jpgname, first=first, last=last)

    if ((n+1) % N_COLUMNS) == 0:
        s += r'\\'
    else:
        s += '&'

    n += 1


textable = table % s
outfile = open('%s/%s.tex' % (FOLDER, TITLE), 'w')
outfile.write(doc % textable)
outfile.close()

pwd = os.path.realpath(os.path.curdir)

# try to also compile to PDF
try:
    os.chdir(FOLDER)
    os.system('pdflatex "%s.tex"' % TITLE)
except e:
    print(e)
    print('Oops, tried to compile to PDF but something happened, sorry!')
finally:
    # ensure we exit in the same directory
    os.chdir(pwd)




