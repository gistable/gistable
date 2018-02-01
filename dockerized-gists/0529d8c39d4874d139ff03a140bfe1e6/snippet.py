#!/usr/bin/python3

from lxml import etree

import os
import tempfile
import urllib

JAVA_VARIABLE_NAME="emergencyNumberPerCountryCode"
PHONE_NUMBER_METADATA_URL="https://raw.githubusercontent.com/googlei18n/libphonenumber/master/resources/ShortNumberMetadata.xml"

def download_phone_number_metadata():
    tmpdir = tempfile.mkdtemp()
    tmpfile = os.path.join(tmpdir, "numbers.metadata")
    urllib.urlretrieve(PHONE_NUMBER_METADATA_URL, tmpfile)
    return tmpfile

def extract_emergency_number_example(metadata_file):
    tree = etree.parse(metadata_file)

    result = {}

    for territory in tree.xpath("/phoneNumberMetadata/territories/territory"):
        country_code = territory.get("id")
        emergency_number_example = territory.xpath("emergency/exampleNumber")

        if len(emergency_number_example) == 1:
           result[country_code] = emergency_number_example.pop().text

    return result

def build_java_definition(emergency_number_per_country_code):
    lines = ["ImmutableMap.Builder<String, String> {} = ImmutableMap.builder();".format(JAVA_VARIABLE_NAME)]

    for key in sorted(emergency_number_per_country_code.keys()):
        lines.append('{}.put("{}", "{}");'.format(JAVA_VARIABLE_NAME, key, emergency_number_per_country_code[key]))

    return '\n'.join(lines)

metadata_file = download_phone_number_metadata()
numbers = extract_emergency_number_example(metadata_file)

print build_java_definition(numbers)

os.remove(metadata_file)
