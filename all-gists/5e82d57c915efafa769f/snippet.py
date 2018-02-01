#!/usr/bin/env python
from __future__ import print_function
import argparse
import collections
import re
import subprocess
import sys


KNOWN_IMPORT_PACKAGE_MAP = {
    'django-statsd-mozilla': ('django_statsd',),
    'pillow': ('pil',),
    'pycrypto': ('crypto',),
    'pyopenssl': ('openssl',),
    'pyxmlsec': ('xmlsec',),
}
KNOWN_REQUIREMENTS = frozenset((
    # modify this as you like
    'coverage',             # build/check
    'flake8',               # build/check
    'ipdb',                 # debug
    'ipython',              # debug
    'pytz',                 # used by django
))

RE_IMPORT_PACKAGE = re.compile(r'^\s*(?:from|import) ([\w]+)')
RE_IMPORT_BLACKLIST = re.compile(r'^(?:__|YOURPROJECT)')
RE_REQUIREMENT = re.compile(r'^([\w-]+)')

Finding = collections.namedtuple('Finding', 'token original line path lineno')

cmdline = argparse.ArgumentParser()
cmdline.add_argument('--explain')
cmdline.add_argument('--fuzzy', action='store_true', default=False)
cmdline.add_argument('--verbose', action='store_true', default=False)


def ifiles():
    output = subprocess.check_output(['git', 'ls-files'])
    for line in output.splitlines():
        if line.endswith('.py'):
            yield line


def parse_imports(path):
    '''File path -> set() of imported package names

    from lib.sub import test
    import subprocess
    ->
    {'lib', 'subprocess'}
    '''
    tokens = {}
    with open(path, 'rb') as f:
        for i, line in enumerate(f, 1):
            # print('line', line)
            m = RE_IMPORT_PACKAGE.match(line)
            if m:
                token = m.group(1)
                # print('token', token)
                if token and not RE_IMPORT_BLACKLIST.match(token) and token not in tokens:
                    f = Finding(
                        token=token.lower(),
                        original=token,
                        line=line.rstrip(),
                        path=path,
                        lineno=i,
                    )
                    tokens[f.token] = f
    return tokens


def parse_requirement_line(line, path, lineno):
    m = RE_REQUIREMENT.match(line)
    if not m:
        return None

    token = m.group(1)
    # print('token', token)
    if not token:
        return None

    return Finding(
        token=token.lower(),
        original=token,
        line=line.rstrip(),
        path=path,
        lineno=lineno,
    )


def parse_requirements(path):
    tokens = {}
    with open(path, 'rb') as f:
        for i, line in enumerate(f, 1):
            # print('line', line)
            f = parse_requirement_line(line, path, i)
            if f and f.token not in tokens:
                tokens[f.token] = f

    return tokens


def explain(req, required, imported, more_fuzzy=False):
    imps = []
    # print('trying to explain', req.line)

    if req.token in KNOWN_REQUIREMENTS:
        imps.append(Finding(
            token=req.token,
            original=req.token,
            line=req.token,
            path='(known)',
            lineno=1,
        ))

    # Try to find required token in imported tokens
    # Django==1.5.8 ~ from django.test import TestCase
    imp = imported.get(req.token)
    if imp:
        imps.append(imp)

    # Try known import-package map
    imp_tokens = KNOWN_IMPORT_PACKAGE_MAP.get(req.token)
    if imp_tokens:
        for imp_token in imp_tokens:
            imp = imported.get(imp_token)
            if imp:
                imps.append(imp)
            # print('found import', imported[imp_token])

    # Try to strip "python" prefix or suffix from package name
    if req.token.startswith('python-') or req.token.endswith('-python'):
        new = req._replace(token=req.token.replace('python', '').strip('-'))
        imps.extend(explain(new, required, imported))

    # django-dynamic-fixture -> django_dynamic_fixture
    if '-' in req.token:
        new = req._replace(token=req.token.replace('-', '_'))
        imps.extend(explain(new, required, imported))

    if more_fuzzy:
        if 'py' in req.token:
            new = req._replace(token=req.token.replace('py', '').strip('-'))
            imps.extend(explain(new, required, imported))
        if 'django' in req.token:
            new = req._replace(token=req.token.replace('django', '').strip('-'))
            imps.extend(explain(new, required, imported))

    return imps


def main():
    flags = cmdline.parse_args()

    required = parse_requirements('requirements.txt')
    # print('required', required.keys())

    imported = {}
    for path in ifiles():
        imported.update(parse_imports(path))
    # print('imported', '\n'.join(sorted(imported.keys())))

    if flags.explain:
        req = parse_requirement_line(flags.explain, '(cmdline)', 1)
        imps = explain(req, required, imported, more_fuzzy=True)
        if not imps:
            print('cannot explain', req.line)
            sys.exit(1)
        for imp in imps:
            print('{req.line} is explained by {imp.path}:{imp.lineno}\t{imp.line}'.format(imp=imp, req=req))
        return

    ok = True
    for req in sorted(required.itervalues(), key=lambda req: req.token):
        imps = explain(req, required, imported, more_fuzzy=flags.fuzzy)
        if not imps:
            print('cannot explain', req.line)
            ok = False
        if flags.verbose:
            for imp in imps:
                print('{req.line} is explained by {imp.path}:{imp.lineno}\t{imp.line}'.format(imp=imp, req=req))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
