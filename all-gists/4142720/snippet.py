#!/usr/bin/env python
# Licensed to Tomaz Muraus under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# Tomaz muraus licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sys

from os.path import join as pjoin
from collections import defaultdict
from optparse import OptionParser

try:
    import matplotlib.pyplot as plt
except ImportError:
    raise ImportError('Missing matplotlib dependency. You can install it' +
                      ' using pip:\n pip install matplotlib')

LEGEND = {
    'sstables': {
        'title': 'Cassandra - Number of accessed SStables per read',
        'x_axis': 'Number of SSTables accessed per read'
     },
    'write_latency': {
        'title': 'Cassandra - Write Latency',
        'x_axis': 'Write latency in ms'
    },
    'read_latency': {
        'title': 'Cassandra - Read Latency',
        'x_axis': 'Read latency in ms'
    },
    'row_size': {
        'title': 'Cassandra - Row size',
        'x_axis': 'Row size in bytes'
    },
    'column_count': {
        'title': 'Cassandra - Column count',
        'x_axis': 'Column count'
    }
}

INDEX_MAP = {
    1: 'sstables',
    2: 'write_latency',
    3: 'read_latency',
    4: 'row_size',
    5: 'column_count'
}

def parse_and_format_data(data):
    lines = data.split('\n')
    result = defaultdict(list)

    for index, line in enumerate(lines):
        if index == 0:
            # header
            continue

        split = re.split('\s+', line)

        if len(split) < 5:
            # bad line
            continue

        if len(split) == 5:
            # Insert 0 for sstable count
            split.insert(1, 0)

        offset = int(split[0])
        for index in range(1, 6):
            key = INDEX_MAP[index]
            value = int(split[index])

            if value != 0:
                result[key].extend([value] * offset)

    return result

def main():
    usage = 'usage: %prog --input=<path to a file with cfhistograms output>' + \
             ' --output=<path to the output directory>'
    parser = OptionParser(usage=usage)
    parser.add_option('--input', dest='input',
                  help='Path to a file with cfhistograms output')
    parser.add_option('--output', dest='output',
                  help='Path to a file where the graphs are saved')

    (options, args) = parser.parse_args()

    if not options.input:
        print('Error: Missing "--input" option')
        print parser.print_usage()
        sys.exit(1)

    if not options.output:
        print('Error: Missing "--output" option')
        print parser.print_usage()
        sys.exit(1)

    if not os.path.exists(options.input) or not \
       os.path.isfile(options.input):
        print('--input argument is not a valid file path')
        sys.exit(2)

    if not os.path.exists(options.output):
        os.makedirs(options.output)

    with open(options.input, 'r') as fp:
        print('Processing file...')

        content = fp.read()
        parsed = parse_and_format_data(content)

        for key, values in LEGEND.items():
            data = parsed[key]
            output_path = pjoin(options.output, '%s_histogram.png' % (key))

            print('Saving histogram: %s' % (output_path))

            plt.title(values['title'])
            plt.ylabel('Frequency')
            plt.xlabel(values['x_axis'])
            plt.hist(data, facecolor='green', alpha=0.75,
                    range=(min(data), max(data)))
            fig = plt.gcf()
            plt.grid(True)
            plt.show()
            plt.draw()
            fig.savefig(output_path, dpi=100)
    pass

main()