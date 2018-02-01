
"""
Given an arbitrarily nested dictionary, create a PyTables Table
Populate a table row given the contents of a dictionary
"""

import tables
import numpy as np
import sys


if sys.version.startswith('3'):
    unicode = str


def get_dtype(data):
    """Given a dict, generate a nested numpy dtype"""
    fields = []
    for (key, value) in data.items():
        # make strings go to the next 64 character boundary
        # pytables requires an 8 character boundary
        if isinstance(value, unicode):
            value += u' ' * (64 - (len(value) % 64))
            # pytables does not support unicode
            if isinstance(value, unicode):
                value = value.encode('utf-8')
        elif isinstance(value, str):
            value += ' ' * (64 - (len(value) % 64))

        if isinstance(value, dict):
            fields.append((key, get_dtype(value)))
        else:
            value = np.array(value)
            fields.append((key, '%s%s' % (value.shape, value.dtype)))
    return np.dtype(fields)


def _recurse_row(row, base, data):
    for (key, value) in data.items():
        new = base + key
        if isinstance(value, dict):
            _recurse_row(row, new + '/', value)
        else:
            row[new] = value


def add_row(tbl, data):
    """Add a new row to a table based on the contents of a dict.
    """
    row = tbl.row
    for (key, value) in data.items():
        if isinstance(value, dict):
            _recurse_row(row, key + '/', value)
        else:
            row[key] = value
    row.append()
    tbl.flush()


if __name__ == '__main__':

    data = dict(a=1, e=dict(c='1', b=[1, 2, 3],
                            f=dict(foo='bar')))
    dtype = get_dtype(data)
    print(dtype)

    fid = tables.open_file('test.h5', 'w')

    grp = fid.create_group('/', 'foo')

    tbl = fid.create_table(grp, 'bar', dtype)

    add_row(tbl, data)

    assert tbl.read(0)['e']['c'].astype(np.str) == '1'
