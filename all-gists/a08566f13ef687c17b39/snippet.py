#!/usr/bin/env python3

"""Parses and encodes the result of `docker ps` in JSON format."""

import json
import sys
from collections import namedtuple
from subprocess import Popen, PIPE


# This assumes output of `docker ps` using Docker 1.3.
# New versions of Docker may have different column names and break this script.
COLUMNS = [
    'CONTAINER ID',
    'IMAGE',
    'COMMAND',
    'CREATED',
    'STATUS',
    'PORTS',
    'NAMES',
]


ColumnRange = namedtuple('ColumnRange', ['column', 'start_idx', 'stop_idx'])


def get_running_containers(args):
    """Finds running Docker containers by parsing the output of `docker ps`."""
    args = ['docker', 'ps'] + args
    out, err = Popen(args, stdout=PIPE, stderr=PIPE).communicate()
    header, *rows = out.decode('utf-8').splitlines()
    column_ranges = [find_column_range(header, column) for column in COLUMNS]
    running_containers = [row_to_container(row, column_ranges) for row in rows]
    return running_containers


def find_column_range(header, column):
    """Determines the string indexes that the given column lies between."""
    column_idx = COLUMNS.index(column)
    start_idx = header.index(column)

    try:
        next_column = COLUMNS[column_idx + 1]
        stop_idx = header.index(next_column)
    except IndexError:
        # There is no next column (i.e. we're on the last one).
        stop_idx = None

    column_range = ColumnRange(column, start_idx, stop_idx)
    return column_range


def row_to_container(row, column_ranges):
    """Extracts the column values from a container row."""
    container = {column_range.column: extract_field(row, column_range)
                 for column_range in column_ranges}
    return container


def extract_field(row, column_range):
    """Pulls the value of a field from a given row."""
    start_idx = column_range.start_idx
    stop_idx = column_range.stop_idx or len(row)
    field = row[start_idx:stop_idx].strip()
    return field


if __name__ == '__main__':
    args = sys.argv[1:]
    running_containers = get_running_containers(args)
    json.dump(running_containers, sys.stdout)