#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# To generate DEB package from Python Package:
# sudo pip3 install stdeb
# python3 setup.py --verbose --command-packages=stdeb.command bdist_deb
#
#
# To generate RPM package from Python Package:
# sudo apt-get install rpm
# python3 setup.py bdist_rpm --verbose --fix-python --binary-only
#
#
# To generate EXE MS Windows from Python Package (from MS Windows only):
# python3 setup.py bdist_wininst --verbose
#
#
# To generate PKGBUILD ArchLinux from Python Package (from PyPI only):
# sudo pip3 install git+https://github.com/bluepeppers/pip2arch.git
# pip2arch.py PackageNameHere
#
#
# To Upload to PyPI by executing:
# sudo pip install --upgrade pip setuptools wheel virtualenv
# python3 setup.py bdist_egg bdist_wheel --universal sdist --formats=zip upload


"""Setup.py for Python, as Generic as possible."""


import logging as log
import os
import re
import sys

from copy import copy
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory, gettempdir
from zipapp import create_archive

from setuptools import Command, find_packages, setup


##############################################################################
# EDIT HERE


DESCRIPTION = ("""

               """)
MODULE_PATH = Path(__file__).parent / "main.py"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
README = Path(__file__).parent / "README.md"
APP_NAME = "myapp"


##############################################################################
# Dont touch below


SOURCE = MODULE_PATH.read_text()
LONG_DESCRIPTION = README.read_text().strip()
PYZ_RUNPY = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from runpy import run_module
print("Running Python module: {0}.")
run_module("{0}")
""".format(APP_NAME)


def find_this(search, source=SOURCE):
    """Take a string and a filename path string and return the found value."""
    print(f"Searching for: '{search}'.")
    if not search or not source:
        print(f"Not found on source: '{search}'.")
        return ""
    return str(re.compile(r'".*__{what}__ = "(.*?)"'.format(
        what=search), re.S).match(source).group(1)).strip()


def parse_requirements(path=REQUIREMENTS_FILE):
    """Rudimentary parser for the requirements.txt file.

    We just want to separate regular packages from links to pass them to the
    'install_requires' and 'dependency_links' params of the 'setup()'.
    """
    print(f"Parsing Requirements from file: {path}.")
    pkgs, links = ["pip"], []
    if not os.path.isfile(path):
        return pkgs, links
    try:
        requirements = map(str.strip, path.splitlines())
    except Exception as reason:
        log.warning(reason)
        return pkgs, links
    for req in requirements:
        if not req:
            continue
        if 'http://' in req.lower() or 'https://' in req.lower():
            links.append(req)
            name, version = re.findall("\#egg=([^\-]+)-(.+$)", req)[0]
            pkgs.append(f"{name}=={version}")
        else:
            pkgs.append(req)
    print(f"Requirements found: {pkgs}, {links}.")
    return pkgs, links


install_requires_list, dependency_links_list = parse_requirements()


class ZipApp(Command):
    """https://docs.python.org/3/library/zipapp.html#zipapp.create_archive ."""
    description, user_options = "Creates a zipapp.", []

    def initialize_options(self): pass  # Dont needed, but required.

    def finalize_options(self): pass  # Dont needed, but required.

    def run(self):
        with TemporaryDirectory() as tmpdir:
            copytree(Path(__file__).parent, os.path.join(tmpdir, APP_NAME))
            fyle = Path(tmpdir).parent / '__main__.py'
            fyle.write_text(PYZ_RUNPY)
            create_archive(tmpdir, APP_NAME + ".pyz", "/usr/bin/env python3")


##############################################################################
# EDIT HERE


setup(

    name="app",
    version=find_this("version"),

    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,

    url=find_this("url"),
    license=find_this("license"),

    author=find_this("author"),
    author_email=find_this("email"),
    maintainer=find_this("author"),
    maintainer_email=find_this("email"),
    download_url="https://github.com/foo/bar/releases",

    include_package_data=True,
    zip_safe=True,

    python_requires='>=3.6,!=3.5.*',
    extras_require={"pip": ["pip"]},
    install_requires=["pip"],
    setup_requires=["pip"],
    tests_require=["pip"],
    requires=["pip"],

    # install_requires=install_requires_list,
    dependency_links=dependency_links_list,

    scripts=["app.py"],

    # What does your project relate to?
    keywords="Some KeyWords Here",

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'sample': ['package_data.dat'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        "console_scripts": ['myapp=myapp.__main__:main'],
    },

    # Make PYZ
    cmdclass={
        "zipapp": ZipApp,
    },


    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        'Development Status :: 6 - Mature',
        'Development Status :: 7 - Inactive',

        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Environment :: Console :: Framebuffer',
        'Environment :: MacOS X',
        'Environment :: MacOS X :: Aqua',
        'Environment :: MacOS X :: Carbon',
        'Environment :: MacOS X :: Cocoa',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: OpenStack',
        'Environment :: Other Environment',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: Mozilla',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: X11 Applications :: GTK',
        'Environment :: X11 Applications :: Gnome',
        'Environment :: X11 Applications :: KDE',
        'Environment :: X11 Applications :: Qt',

        'Framework :: AsyncIO',
        'Framework :: Bottle',
        'Framework :: Buildout',
        'Framework :: Buildout :: Extension',
        'Framework :: Buildout :: Recipe',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Flake8',
        'Framework :: Flask',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Framework :: Pytest',
        'Framework :: Scrapy',
        'Framework :: Setuptools Plugin',
        'Framework :: Sphinx',
        'Framework :: Sphinx :: Extension',
        'Framework :: Sphinx :: Theme',
        'Framework :: Tryton',
        'Framework :: TurboGears :: Applications',
        'Framework :: TurboGears :: Widgets',
        'Framework :: Twisted',

        'Intended Audience :: Customer Service',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',

        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'License :: Free For Educational Use',
        'License :: Free For Home Use',
        'License :: Free To Use But Restricted',
        'License :: Free for non-commercial use',
        'License :: Freely Distributable',
        'License :: Freeware',
        'License :: OSI Approved',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: Artistic License',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: Common Public License',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'License :: OSI Approved :: GNU Free Documentation License (FDL)',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'License :: OSI Approved :: Python License (CNRI Python License)',
        'License :: OSI Approved :: Python Software Foundation License',
        'License :: OSI Approved :: Qt Public License (QPL)',
        'License :: OSI Approved :: Universal Permissive License (UPL)',
        'License :: OSI Approved :: W3C License',
        'License :: OSI Approved :: zlib/libpng License',
        'License :: Other/Proprietary License',
        'License :: Public Domain',

        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: German',
        'Natural Language :: Hindi',
        'Natural Language :: Italian',
        'Natural Language :: Japanese',
        'Natural Language :: Korean',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Russian',
        'Natural Language :: Spanish',
        'Natural Language :: Swedish',

        'Operating System :: Android',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows Server 2008',
        'Operating System :: OS Independent',
        'Operating System :: Other OS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: BSD :: BSD/OS',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: BSD :: NetBSD',
        'Operating System :: POSIX :: BSD :: OpenBSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Other',
        'Operating System :: Unix',
        'Operating System :: iOS',

        'Programming Language :: Assembly',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Programming Language :: Cython',
        'Programming Language :: JavaScript',
        'Programming Language :: Objective C',
        'Programming Language :: Other',
        'Programming Language :: Other Scripting Engines',
        'Programming Language :: PL/SQL',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: MicroPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Ruby',
        'Programming Language :: Rust',
        'Programming Language :: SQL',
        'Programming Language :: Unix Shell',

        'Topic :: Adaptive Technologies',
        'Topic :: Artistic Software',
        'Topic :: Communications',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Topic :: Communications :: Conferencing',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Address Book',
        'Topic :: Communications :: Email :: Email Clients (MUA)',
        'Topic :: Communications :: Email :: Filters',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Topic :: Communications :: Email :: Mailing List Servers',
        'Topic :: Communications :: Email :: Post-Office',
        'Topic :: Communications :: Email :: Post-Office :: IMAP',
        'Topic :: Communications :: Email :: Post-Office :: POP3',
        'Topic :: Communications :: File Sharing',
        'Topic :: Communications :: Ham Radio',
        'Topic :: Communications :: Internet Phone',
        'Topic :: Communications :: Telephony',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Database :: Front-Ends',
        'Topic :: Desktop Environment',
        'Topic :: Desktop Environment :: File Managers',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Desktop Environment :: K Desktop Environment (KDE)',
        'Topic :: Desktop Environment :: K Desktop Environment (KDE) :: Themes',
        'Topic :: Desktop Environment :: Screen Savers',
        'Topic :: Desktop Environment :: Window Managers',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Education',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Education :: Testing',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Games/Entertainment :: First Person Shooters',
        'Topic :: Games/Entertainment :: Fortune Cookies',
        'Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Games/Entertainment :: Real Time Strategy',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Games/Entertainment :: Turn Based Strategy',
        'Topic :: Home Automation',
        'Topic :: Internet',
        'Topic :: Internet :: File Transfer Protocol (FTP)',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Wiki',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Internet :: WWW/HTTP :: Session',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Internet :: XMPP',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Multimedia :: Graphics :: Capture',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        'Topic :: Multimedia :: Graphics :: Capture :: Scanners',
        'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
        'Topic :: Multimedia :: Graphics :: Editors',
        'Topic :: Multimedia :: Graphics :: Editors :: Raster-Based',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Multimedia :: Sound/Audio :: Editors',
        'Topic :: Multimedia :: Sound/Audio :: Mixers',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Capture',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Office Suites',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Printing',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Artificial Life',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Topic :: Sociology',
        'Topic :: Sociology :: Genealogy',
        'Topic :: Sociology :: History',
        'Topic :: Software Development',
        'Topic :: Software Development :: Assemblers',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Disassemblers',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Ruby Modules',
        'Topic :: Software Development :: Libraries :: pygame',
        'Topic :: Software Development :: Localization',
        'Topic :: Software Development :: Object Brokering',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Testing :: Traffic Generation',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: Software Development :: Version Control :: Mercurial',
        'Topic :: System',
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Archiving :: Compression',
        'Topic :: System :: Archiving :: Mirroring',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Benchmark',
        'Topic :: System :: Boot',
        'Topic :: System :: Clustering',
        'Topic :: System :: Console Fonts',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Emulators',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Hardware',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Hardware :: Mainframes',
        'Topic :: System :: Hardware :: Symmetric Multi-processing',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Firewalls',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Networking :: Monitoring :: Hardware Watchdog',
        'Topic :: System :: Networking :: Time Synchronization',
        'Topic :: System :: Operating System',
        'Topic :: System :: Operating System Kernels',
        'Topic :: System :: Operating System Kernels :: BSD',
        'Topic :: System :: Operating System Kernels :: Linux',
        'Topic :: System :: Power (UPS)',
        'Topic :: System :: Recovery Tools',
        'Topic :: System :: Shells',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: System Shells',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
        'Topic :: Terminals',
        'Topic :: Terminals :: Serial',
        'Topic :: Terminals :: Telnet',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
        'Topic :: Text Editors',
        'Topic :: Text Editors :: Documentation',
        'Topic :: Text Editors :: Emacs',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Editors :: Word Processors',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Fonts',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Markup :: SGML',
        'Topic :: Text Processing :: Markup :: VRML',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Utilities',
    ],

)
