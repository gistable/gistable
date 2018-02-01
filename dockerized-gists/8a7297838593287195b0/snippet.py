# -*- coding: utf-8; -*-
# vi: set encoding=utf-8

import sys
import json


def main(source):
    with open(source) as fp:
        d = json.load(fp)
        for country in d['features']:
            print(json.dumps(dict(
                id=country['id'],
                name=country['properties']['name'],
                geometry=country['geometry'],
            )))


if __name__ == '__main__':
    """
    This script converts the ``countries.geo.json`` from
    `johan/world.geo.json<https://github.com/johan/world.geo.json/blob/master/countries.geo.json>`_
    into JSON that can be imported into Crate.IO

    Usage: python convert.py countries.geo.json | gzip -vc > countries.json
    """
    main(*sys.argv[1:])