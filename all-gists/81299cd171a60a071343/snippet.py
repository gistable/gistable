#!/usr/bin/env python
"""
A quick script for tidying up data from the HealthKit export file.

To get an export file:
 1) Open the Health app on iOS
 2) Under "Health Data", select "All"
 3) Use the share button to get a copy of your data in XML format

This script allows you to get data for one particular value, and turn it into
a slightly more human-readable form.

Use `get_available_types()` to get a list of all the `type` keys used in the
XML data. Find the one you want, and then pass that into
`get_values_for_type()`. I'm assuming that the data is an integer; if that's
not correct, change lines 48 and 55.

The `main()` function has an example for getting step count data.
"""

from collections import defaultdict
from xml.etree import ElementTree as ET

from dateutil import parser


def get_available_types(filepath):
    """
    Returns a list of all the types of data in the HealthKit export file.
    """
    types = set()
    tree = ET.parse("export.xml")
    root = tree.getroot()
    for child in root:
        types.add(child.attrib.get("type", ""))
    types.remove("")
    return types


def get_values_for_type(filepath, type_name):
    """
    Given a path to an XML file, return a list of date/value pairs for all the
    data points of a given type.
    """
    tree = ET.parse("export.xml")
    root = tree.getroot()

    values = defaultdict(int)

    for child in root:
        if child.tag in ["ExportDate", "Me"]:
            continue
        if child.attrib["type"] == type_name:
            date = parser.parse(child.attrib['startDate']).date()
            values[date] += int(float(child.attrib['value']))

    return values


def main():
    step_data = get_values_for_type("export.xml",
                                    "HKQuantityTypeIdentifierStepCount")
    with open("stepdata.txt", "w") as f:
        for date, step_count in step_data.iteritems():
            f.write("%s %s\n" % (date, step_count))


if __name__ == '__main__':
    main()
