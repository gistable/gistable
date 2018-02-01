#!/usr/local/bin/python3
"""Taskpaper to pdf using pandoc.

See http://leancrew.com/all-this/2015/06/putting-the-paper-in-taskpaper/
"""
import argparse
import contextlib
import re
import subprocess
import sys
import tempfile

# Regular expressions. Note: the archive RE assumes that the Archive project
# will be at the end of the file, which is where TaskPaper puts it.
RE_ARCHIVE = re.compile(r'^Archive:.*$', re.DOTALL | re.MULTILINE)
RE_PROJECT = re.compile(r'^(.+):$', re.MULTILINE)
RE_TASK    = re.compile(r'^\t(\-.+)$', re.MULTILINE)
PANDOC = '/usr/local/bin/pandoc'
LATEX_TEMPLATE = r"""
\documentclass{article}
\usepackage[landscape,
            left=1in, top=0.5in,
            bottom=0.5in, right=4.5in]{geometry}
\usepackage{amssymb}
\usepackage{titlesec}
\providecommand\tightlist{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\titleformat{\section}
  {\normalfont\bfseries}{\thesection}{1em}{}
\titlespacing{\section}{0pt}{50pt plus 28pt minus 18pt}{12pt}
\usepackage{fontspec}
\setmainfont{Source Code Pro}
\usepackage{multicol}
\raggedright
\setcounter{secnumdepth}{0}
\renewcommand\labelitemi{$$\square$$}
\pagestyle{empty}

\begin{document}
\begin{multicols}{2}
$body$
\end{multicols}
\end{document}
"""

@contextlib.contextmanager
def temporary_template_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.latex') as fh:
        fh.write(LATEX_TEMPLATE)
        fh.flush()
        yield fh.name


def main():
    parser = argparse.ArgumentParser('Convert taskpaper to pdf')
    parser.add_argument('filename', type=argparse.FileType('r'))
    args = parser.parse_args()
    taskpaper = args.filename.read()

    # Grab the TaskPaper data, delete the archive, and turn the rest into
    # Markdown.
    md = RE_ARCHIVE.sub('', taskpaper)
    md = RE_PROJECT.sub(r'\n# \1\n', md)
    md = RE_TASK.sub(r'\1', md)

    with temporary_template_file() as temp:
        p = subprocess.Popen(
                [PANDOC, '-o', 'taskpaper.pdf', '-f', 'markdown', '--template', temp,
                 '--latex-engine=xelatex'],
                stdin=subprocess.PIPE)
        p.communicate(md.encode('utf-8'))


if __name__ == '__main__':
    sys.exit(main())
