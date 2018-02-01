#! /usr/bin/env python
#
# coding: utf-8
"""
Version-bump script for Maven projects.
Reads pom.xml, parses the version, increments it and writes an updated pom to stdout.

Usage:
    pom-vbump.py [-i] [-v <new version number>] [path to pom.xml]

Options:
    -n  Dry run: just print the new version number that would be written to pom.xml
    -i  Edit pom.xml in place, instead of writing result to stdout
    -v  specify a version number, e.g. "1.23"

If the next version number (v_n) is not specified, it will be guestimated from
the current version (v_c) using the following rules:
    - if v_c is of the form 'a-SNAPSHOT',
        remove the '-SNAPSHOT' part, so v_n = a
    - if v_c is of the form 'a.b.c...z' where z is an integer,
        increment z and add '-SNAPSHOT', so v_n = a.b.c...(z+1)-SNAPSHOT
    - otherwise give up and throw an error

If pom.xml file is not specified, the script will look in the current working directory.

Tested with Python 2.7.5 and 3.3.2.
Requires lxml.
"""
import sys
import getopt
import os.path
from lxml import etree as ET

class InvalidVersion(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return "Invalid version: " + self.msg


def main(args):
    next_version = None
    in_place = False
    dry_run = False
    pom_xml = './pom.xml'

    try:
        opts, args = getopt.getopt(args, 'nv:ih', ['dryrun', 'version', 'inplace', 'help'])
    except getopt.GetoptError:
        usage()
        return False

    for opt, value in opts:
        if opt in ('-h', '--help'):
            usage()
            return False
        elif opt in ('-v', '--version'):
            next_version = value
        elif opt in ('-i', '--inplace'):
            in_place = True
        elif opt in ('-n', '--dryrun'):
            dry_run = True
        else:
            usage()
            return False

    if len(args) > 0:
        pom_xml = args[0]
    if not os.path.isfile(pom_xml):
        log("ERROR: Could not find pom.xml file: %s" %pom_xml)
        usage()
        return False

    try:
        bump(pom_xml, next_version, in_place, dry_run)
        return True
    except InvalidVersion as e:
        log(e)
        return False

def usage():
    print(__doc__)

def bump(pom_xml, next_version, in_place, dry_run):
    log("Parsing %s..." % pom_xml)

    parser = ET.XMLParser(remove_comments=False)
    xml = ET.parse(pom_xml, parser=parser)

    # Find the project's current version
    version_tag = xml.find("./{*}version")
    if version_tag == None:
        raise InvalidVersion("pom.xml does not appear to have a <version> tag")
    current_version = version_tag.text
    log("Current version is %s" % current_version)

    # Calculate the next version, if not specified
    if not next_version:
        next_version = increment_version(current_version)

    # If dry run, just print the next version and exit
    if dry_run:
        print next_version
    else:
        log("Incrementing version to %s" % next_version)

        # Update the XML
        version_tag.text = next_version

        if in_place:
            # Write back to pom.xml
            write_xml_to_file(xml, pom_xml)
        else:
            # Print result to stdout
            print_xml(xml)


def increment_version(current_version):
    # If it's a snapshot version, convert it to a release version
    if current_version.endswith('-SNAPSHOT'):
        return current_version[:-9]

    parts = current_version.split(".")
    last_part = parts[len(parts) - 1]
    try:
        # Add one to the final part of the version string
        incremented_last_part = str(int(last_part) + 1)
    except TypeError:
        raise InvalidVersion("Unsuppported version format [%s]" % current_version)

    # Try to maintain the zero padding of the old version, if any
    incremented_last_part = incremented_last_part.zfill(len(last_part))

    # Make it a snapshot version
    incremented_last_part = incremented_last_part + '-SNAPSHOT'

    return ".".join(parts[:-1] + [incremented_last_part])

def write_xml_to_file(xml, output_file):
    with open(output_file, 'wb') as f:
        f.write(ET.tostring(xml, encoding="utf-8", xml_declaration=True))

def print_xml(xml):
    result = ET.tostring(xml, encoding="utf-8", xml_declaration=True)
    if sys.hexversion >= 0x03000000:
        # Python 3.x
        sys.stdout.buffer.write(result)
    else:
        # Python 2.x
        print(result)

def log(msg):
    sys.stderr.write(str(msg) + '\n')

if __name__ == '__main__':
    sys.exit(not main(sys.argv[1:]))
