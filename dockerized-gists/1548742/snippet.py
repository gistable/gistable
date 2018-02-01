#!/usr/bin/python
# -*- coding: utf-8

import ConfigParser
import argparse
import getpass
import os
import shlex
import subprocess
import sys

from jinja2 import Template
import virtualenv


class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    EC = '\033[0m'


test_settings = Template('''
from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

INSTALLED_APPS += ('{{name}}',)

{% if use_nose %}
INSTALLED_APPS += ('django_nose',)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['{{name}}',
    '--cover-erase',
    '--cover-package={{name}}',
    '--cover-tests',
    '--failed',
    '--stop',
    {% if jenkins %}'--with-xcoverage',
    '--with-xunit',
    {% else %}'--with-coverage',{% endif %}
]
{% endif %}
''')

st = Template('''#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import sys
from fnmatch import fnmatchcase

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from distutils.core import setup, find_packages, Command

from distutils.util import convert_path


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.py', '*.pyc', '*$py.class', '*~', '.*', '*.bak')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')


# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Note: you may want to copy this into your setup.py file verbatim, as
# you can't import this from another package, when you don't know if
# that package is installed yet.
def find_package_data(
    where='.', package='',
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """

    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, '__init__.py'))
                    and not prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/', package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out


class RunTests(Command):
    description = "Run the django test suite from the test_project dir."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        this_dir = os.getcwd()
        testproj_dir = os.path.join(this_dir, "test_project")
        os.chdir(testproj_dir)
        sys.path.append(testproj_dir)
        from django.core.management import execute_manager
        os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
                "DJANGO_SETTINGS_MODULE", "test_settings")
        settings_file = os.environ["DJANGO_SETTINGS_MODULE"]
        settings_mod = __import__(settings_file, {}, {}, [''])
        execute_manager(settings_mod, argv=[
            __file__, "test"])
        os.chdir(this_dir)


setup(
    author="{{author}}",
    author_email="{{email}}",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    cmdclass = {"test": RunTests},
    description="{{description}}",
    install_requires = [
        {% for p in pkgs %}'{{p}}',
        {% endfor %}
    ],
    long_description=read('README.rst'),
    name = "{{name}}",
    package_data = find_package_data(),
    packages = find_packages(exclude=['test_project']),
    version = "0.1",
    zip_safe=False,
)
''')


git_ignore = Template('''*.py[oc]
*.swp
*.log
*.db
*.tar.gz
*.egg-info/
build/
dist/
env/
.DS_Store
.noseids
.coverage
test.db
{% if jenkins %}test_project/coverage.xml
test_project/nosetests.xml{% endif %}
''')


def create_app(name, description, author, email, 
        app_name=None, reqs=None, init_git=False,
        jenkins=False):

    if os.path.exists(name):
        print(color.FAIL + ('Project path %s exists' % name) + color.EC)
        sys.exit(1)

    print(color.OKBLUE + ('Creating project path for %s' % name) + color.EC)
    os.makedirs('%s' % (name))

    org_path = os.path.realpath(name)

    with open('%s/README.rst' % name, 'w') as f:
        f.write('')

    venv = os.path.join(os.path.realpath(name), 'env')
    virtualenv.create_environment(venv, site_packages=False)

    print(color.OKGREEN + ('CHDIR %s' % name) + color.EC)
    os.chdir(name)
    print(color.OKGREEN + ('Installing pip and requirements') + color.EC)

    reqs = reqs or []
    reqs.append('django')

    for x in [
            'pip install -E %s %s' % (venv, ' '.join(set(reqs))),
            '%s/bin/django-admin.py startproject test_project' % (venv)]:

        print(color.WARNING + ('Executing "%s"' % x) + color.EC)

        c = subprocess.Popen(shlex.split(x),
            stdin=subprocess.PIPE,
            stdout=sys.stdout)
        o, e = c.communicate()
        if e:
            print(color.FAIL + e + color.EC)
            sys.exit(1)

    print(color.OKGREEN + ('Creating test_project and app') + color.EC)

    os.chdir('test_project')

    for x in [
            '%s/bin/python manage.py startapp %s' % (venv, (app_name or name)),
            'mv %s ../' % (app_name or name)]:

        print(color.WARNING + ('Executing "%s"' % x) + color.EC)

        c = subprocess.Popen(shlex.split(x),
            stdin=subprocess.PIPE,
            stdout=sys.stdout)
        o, e = c.communicate()
        if e:
            print(color.FAIL + e + color.EC)
            sys.exit(1)

    os.chdir(org_path)

    if init_git:

        print(color.WARNING + ('Initializing git') + color.EC)

        c = subprocess.Popen(shlex.split('git init'),
            stdin=subprocess.PIPE,
            stdout=sys.stdout)
        o, e = c.communicate()
        if e:
            print(color.FAIL + e + color.EC)
            sys.exit(1)

        with open('.gitignore' , 'w') as f:
            f.write(git_ignore.render(jenkins=jenkins))

    c = subprocess.Popen('source %s/bin/activate && pip freeze' % venv,
        stdout=subprocess.PIPE,
        shell=True)
    o, e = c.communicate()
    
    with open('setup.py', 'w') as f:
        f.write(st.render(name=(app_name or name), description=description,
            email=email, author=author, pkgs=[i.strip() 
                for i in o.split('\n') if i.strip()]))

    with open('test_project/test_settings.py', 'w') as f:
         f.write(test_settings.render(name=(app_name or name), 
            use_nose=('django-nose' in reqs), jenkins=jenkins))

    print(color.OKGREEN + ('Finished') + color.EC)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Creates a setuptools installable django application.')

    parser.add_argument('name', metavar='name', type=str,
        help='Name')
    parser.add_argument('--description', metavar='description', type=str,
        help='Description', default='', required=False)
    parser.add_argument('--app', metavar='app', type=str,
        help='Application name', default=None, required=False)
    parser.add_argument('--author', metavar='author', type=str,
        help='Author', default=None, required=False)
    parser.add_argument('--email', metavar='email', type=str,
        help='Email', default=None, required=False)

    parser.add_argument('--git', help='Initialize a git repo',
        default=False, action='store_true', required=False)
    parser.add_argument('--nose', help='Configure nose',
        default=False, action='store_true', required=False)
    parser.add_argument('--jenkins', help='Configure jenkins',
        default=False, action='store_true', required=False)

    args = parser.parse_args()
    author, email = args.author, args.email

    if None in [author, email]:
        config_path = os.path.expanduser('~/.pjutils')
        if not os.path.isfile(config_path):
            import socket
            author = author or getpass.getuser()
            email = email or '%s@%s' % (author, socket.gethostname())
        else:
            config = ConfigParser.RawConfigParser(allow_no_value=True)
            config.readfp(open(os.path.expanduser('~/.pjutils')))
            author = config.get('defaults', 'author')
            email = config.get('defaults', 'email')

    reqs = ['django-nose', 'coverage'] if args.nose else None

    if args.jenkins and args.nose:
        reqs.append('nosexcover')

    create_app(args.name, args.description, author, email,
        reqs=reqs, init_git=args.git, app_name=args.app, 
        jenkins=args.jenkins)
