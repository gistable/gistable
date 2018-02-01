# -*- coding: utf-8 -*-
"""Prettify JSON

Usage:

    pjson --help
    pjson --test
    cat my.json | pjson

"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import json

import datetime as dt
import functools as ft

# TODO (mb 2016-09-14): preserve ordering of keys
PY2 = sys.version_info.major < 3

if PY2:
    INT_TYPES = (int, long)                                         # noqa
    NUM_TYPES = (int, long, float)                                  # noqa
    BASIC_TYPES = (unicode, bytes, int, long, float, type(None))    # noqa
    str = unicode                                                   # noqa
else:
    INT_TYPES = (int,)
    NUM_TYPES = (int, float)
    BASIC_TYPES = (str, bytes, int, float, type(None))
    str = str


def _get_alignment_fmt(values, val_strings, is_key=False):
    fmt = "{}"

    if all(isinstance(v, INT_TYPES) for v in values):
        # align to the right
        fmt = "{{:>{}}}".format(max(map(len, val_strings)))
        use_raw_vals = True
    elif all(isinstance(v, float) for v in values):
        # align by decimal
        fmt = "{{:{}.{}f}}".format(
            max(map(len, val_strings)),
            max((len(v.split(".")[-1]) for v in val_strings)),
        )
        if is_key:
            fmt = '"{}"'.format(fmt)
        use_raw_vals = True
    elif all(isinstance(v, (str, bytes)) for v in values):
        # align to the left
        fmt = "{{:<{}}}".format(max(map(len, val_strings)))
        use_raw_vals = False
    else:
        use_raw_vals = False

    return fmt, use_raw_vals


def dumps(
        data,
        indent=4,
        sort_keys=True,
        max_elem_len=60,
        align=True,
        _depth=1,
        sorted_key=None,
        encoding='utf-8'):

    _dumps = ft.partial(
        dumps,
        indent=indent,
        sort_keys=sort_keys,
        max_elem_len=max_elem_len,
        align=align,
        _depth=_depth + 1,
        sorted_key=sorted_key,
        encoding=encoding
    )
    if isinstance(data, bytes):
        data = data.decode(encoding)

    pad = indent * " "
    if isinstance(data, (tuple, list)):
        # decode all bytes values
        data = [(v.decode(encoding) if isinstance(v, bytes) else v) for v in data]
        sub_elems = [_dumps(v) for v in data]
        total_len = 2 + len(sub_elems) * 2 + sum(map(len, sub_elems))
        has_container_types = any(isinstance(v, (tuple, list, dict)) for v in data)
        if total_len <= max_elem_len and not has_container_types:
            joiner = ", "
            prefix = "["
            suffix = "]"
        else:
            joiner = ",\n" + _depth * pad
            prefix = "[\n" + _depth * pad
            suffix = "\n" + (_depth - 1) * pad + "]"
    elif isinstance(data, dict):
        # decode all bytes keys and values
        dict_type = type(data)
        try:
            dec_data = dict_type()
        except:
            dec_data = data.copy()
            dec_data.clear()

        for k, v in data.items():
            dec_key = k.decode(encoding) if isinstance(k, bytes) else k
            dec_val = v.decode(encoding) if isinstance(v, bytes) else v
            dec_data[dec_key] = dec_val

        sub_items = {json.dumps(k): json.dumps(v) for k, v in data.items()}
        keys_len = sum(map(len, sub_items.keys()))
        vals_len = sum(map(len, sub_items.values()))
        total_len = 2 + len(sub_items) * 4 + keys_len + vals_len

        k_fmt = v_fmt = "{}"

        use_raw_keys = False
        use_raw_vals = False
        if align and all(isinstance(k, BASIC_TYPES) for k in data.keys()):
            k_fmt, use_raw_keys = _get_alignment_fmt(data.keys(), sub_items.keys(), is_key=True)

        if total_len <= max_elem_len or len(sub_items) < 2:
            joiner = ", "
            prefix = "{"
            suffix = "}"
            if sort_keys:
                keys = sorted(data.keys(), key=sorted_key)
            else:
                keys = list(data.keys())

            sub_item_output = [
                (json.dumps(k), _dumps(data[k], _depth=_depth))
                for k in keys
            ]
        else:
            if align:
                if all(isinstance(v, NUM_TYPES) for v in data.values()):
                    v_fmt, use_raw_vals = _get_alignment_fmt(data.values(), sub_items.values())
            else:
                k_fmt = v_fmt = "{}"

            joiner = ",\n" + _depth * pad
            prefix = "{\n" + _depth * pad
            suffix = "\n" + (_depth - 1) * pad + "}"
            if sort_keys:
                keys = sorted(data, key=sorted_key)
            else:
                keys = data.keys()
            sub_item_output = [
                (
                    (k if use_raw_keys else json.dumps(k)),
                    (data[k] if use_raw_vals else _dumps(data[k])),
                )
                for k in keys
            ]

        kv_fmt = k_fmt + ": " + v_fmt
        sub_elems = [kv_fmt.format(*k_v) for k_v in sub_item_output]
    elif isinstance(data, (dt.datetime, dt.date)):
        return '"' + data.isoformat() + '"'
    elif isinstance(data, BASIC_TYPES):
        return json.dumps(data)
    else:
        raise TypeError("'{}' is not a searializable type.".format(type(data)))

    return prefix + joiner.join(sub_elems) + suffix


loads = json.loads


def main(args):
    if '--help' in args:
        print(__doc__)
        return 0

    kwargs = dict(
        kv.lstrip("-").replace("-", "_").split("=")
        for kv in args if "=" in kv
    )
    for k, v in list(kwargs.items()):
        if v.isdigit():
            kwargs[k] = int(v)
    in_data_raw = sys.stdin.read()
    if in_data_raw:
        in_data = loads(in_data_raw)
        print(dumps(in_data, **kwargs))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
