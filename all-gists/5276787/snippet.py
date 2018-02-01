#
# Copyright 2013 by Vinay Sajip.
# Licensed to the Python Software Foundation under a contributor agreement.
#
'''
Usage: pyzzer.py [options] DIRS

Convert Python source directories to runnable zip files.

Options:
  -h, --help      show this help message and exit
  -p FILENAME     Specify a file to prepend to the archive. (Do not specify
                  with -s / --shebang.)
  -s SHEBANG      Specify a shebang line to prepend to the archive. (Do not
                  specify with -p / --prepend.). Defaults to "#!/usr/bin/env
                  python".
  -e MODULE:ATTR  Specify a callable which is the main entry point.
  -x REGEX        Specify regexes to exclude from the zip  (can specify more
                  than once).
  -m FILENAME     Specify modules to add to the root of the zip  (can specify
                  more than once).
  -o FILENAME     Specify the path of the file to write to. If no extension is
                  specified, ".pyz" will be used, or ".pyzw" if -w is
                  specified. If nothing is specified, defaults to the basename
                  of the first directory argument.
  -v              Provide information about progress.
  -w              Use a ".pyzw" extension.
'''

from io import BytesIO
import optparse # support 2.6
import os
import re
import sys
import zipfile

MAIN_TEMPLATE = '''if __name__ == '__main__':
    import sys

    def _resolve(module, func):
        __import__(module)
        mod = sys.modules[module]
        parts = func.split('.')
        result = getattr(mod, parts.pop(0))
        for p in parts:
            result = getattr(result, p)
        return result

    try:
        func = _resolve('%s', '%s')
        rc = func() # None interpreted as 0
    except Exception as e:
        sys.stderr.write('%%s\\n' %% e)
        raise
        rc = 1
    sys.exit(rc)
'''

CALLABLE_RE = re.compile('(?P<mod>\w+(\.\w+)*):(?P<func>\w+(\.\w+)*)')

DEFAULT_SHEBANG = '#! /usr/bin/env python'

def main():
    parser = optparse.OptionParser(usage='%prog [options] DIRS\n\nConvert '
                                         'Python source directories to '
                                         'runnable zip files.')
    parser.add_option('-p', dest='prepend', metavar='FILENAME',
                      help='Specify a file to prepend to the archive. (Do '
                           'not specify with -s / --shebang.)')
    parser.add_option('-s', dest='shebang', metavar='SHEBANG',
                      default=DEFAULT_SHEBANG,
                      help='Specify a shebang line to prepend to the archive. '
                           '(Do not specify with -p / --prepend.). Defaults '
                           'to "#!/usr/bin/env python".')
    parser.add_option('-e', dest='main', metavar='MODULE:ATTR',
                      help='Specify a callable which is the main entry point.')
    parser.add_option('-x', dest='exclude', metavar='REGEX',
                      action='append',
                      help='Specify regexes to exclude from the zip '
                      ' (can specify more than once).')
    parser.add_option('-m', dest='modules', metavar='FILENAME',
                      action='append',
                      help='Specify modules to add to the root of the zip '
                           ' (can specify more than once).')
    parser.add_option('-o', dest='output', metavar='FILENAME',
                      help='Specify the path of the file to write to. If no '
                           'extension is specified, ".pyz" will be used, or '
                           '".pyzw" if -w is specified. If nothing is '
                           'specified, defaults to the basename of the first '
                           'directory argument.')
    parser.add_option('-v', dest='verbose', default=False,
                      action='store_true',
                      help='Provide information about progress.')
    parser.add_option('-w', dest='windowed', default=False,
                      action='store_true',
                      help='Use a ".pyzw" extension.')
    options, args = parser.parse_args()
    if not args:
        parser.print_help()
        return 1
    if (options.prepend and options.shebang and
        options.shebang is not DEFAULT_SHEBANG):
        print('--prepend and --shebang options are mutually exclusive.')
        return 2
    if options.shebang:
        options.shebang = os.linesep.join([options.shebang,
                                           #'# -*- coding: iso-8859-1 -*-',
                                           '# Built with pyzzer.py'])
    if options.main:
        m = CALLABLE_RE.match(options.main)
        if not m:
            raise ValueError('Malformed -e: %s' % options.main)
        d = m.groupdict()
        module, func = d['mod'], d['func']
    if options.output:
        output = options.output
    else:
        output = os.path.basename(args[0])
    n, e = os.path.splitext(output)
    if not e:
        if options.windowed:
            extn = '.pyzw'
        else:
            extn = '.pyz'
        output += extn
    # We could write to the output directly, but writing to an in-memory
    # buffer will aid in debugging
    zip_data = BytesIO()
    if options.prepend:
        with open(options.prepend, 'rb') as f:
            data = f.read()
        zip_data.write(data)
    elif options.shebang:
        shebang = options.shebang + os.linesep
        zip_data.write(shebang.encode('utf-8'))
    if not options.exclude:
        excluded = []
    else:
        excluded = [re.compile(e) for e in options.exclude]

    zf = zipfile.ZipFile(zip_data, 'w', zipfile.ZIP_DEFLATED)
    # ZipFile is not a context manager in 2.6.
    try:
        seen = set()
        for arg in args:
            arg = os.path.abspath(arg)
            if not os.path.isdir(arg):
                raise ValueError('Not a directory: %s', arg)
            fn = os.path.join(arg, '__init__.py')
            if os.path.exists(fn):
                base = os.path.dirname(arg)
            else:
                base = arg
            for root, dirs, files in os.walk(arg):
                for vcsdir in ('.hg', '.git', '.svn'):
                    if vcsdir in dirs:
                        dirs.remove(vcsdir)
                for fn in files:
                    if fn in ('.hgignore', '.gitignore'):
                        continue
                    elif fn.endswith(('.pyc', '.pyo')):
                        continue
                    path = os.path.join(root, fn)
                    skip = False
                    for e in excluded:
                        if e.search(path):
                            skip = True
                            break
                    if skip:
                        continue
                    rp = os.path.relpath(path, base)
                    if rp in seen:
                        raise ValueError('Already added to zip: %s', rp)
                    seen.add(rp)
                    zf.write(path, rp)
                    if options.verbose:
                        print(rp)
        if options.modules:
            for path in options.modules:
                rp = os.path.basename(path)
                if rp in seen:
                    raise ValueError('Already added to zip: %s', rp)
                seen.add(rp)
                zf.write(path, rp)
                if options.verbose:
                    print(rp)

        if '__main__.py' not in seen:
            if not options.main:
                raise ValueError('No __main__.py and -e not specified.')
            s = MAIN_TEMPLATE % (module, func)
            zf.writestr('__main__.py', s.encode('utf-8'))
    finally:
        zf.close()
    with open(output, 'wb') as f:
        f.write(zip_data.getvalue())

if __name__ == '__main__':
    try:
        rc = main()
    except Exception as e:
        print('Failed: %s' % e)
        rc = 9
    sys.exit(rc)