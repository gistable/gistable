
"""
Extract unique Python-Exceptions with their Traceback from a log/text file.

Usage::

    python extract_exceptions.py -f logfile.txt

Furthermore it supports excluding exceptions you don't want to have::

    python extract_exceptions.py -f logfile.txt -e ValueError,AttributeError

Would exclude any ``ValueError`` or ``AttributeError`` from the list.
"""
from optparse import OptionParser


parser = OptionParser()
parser.add_option('-f', '--file', dest='file',
                  help='The file to extract exceptions from',
                  default="",
                  metavar='FILE')
parser.add_option('-e', '--exclude', dest='exclude_list',
                  help='Exclude certain exceptions from output.',
                  default="",
                  metavar='Exception,Exception,...')
options, args = parser.parse_args()


bufMode = False
buf = ''
errors = []

with open(options.file, 'r') as f:
    for line in f:
        if 'Traceback' in line:
            bufMode = True
            continue
        # Usually a Traceback includes a new line at the end, therefore
        # a check for line length should be safe. However this might bite
        # you ;-)
        if line and len(line) < 5:
            bufMode = False
            errors.append(buf)
            buf = ''
        if bufMode:
            # Truncate lines longer than 400 characters.
            if len(line) > 400:
                line = line[:400]+'...\n'
            buf += line

unique_errs = set(errors)
excludes = []
if options.exclude_list:
    excludes = options.exclude_list.split(',')
for err in unique_errs:
    if any([excl in err for excl in excludes]):
        continue
    if err.strip() == "":
        continue
    print err
    print "---"