#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
from math import log10, sqrt


def prune(seq, key, dist):
    pruned = []
    n = 0
    for x in sorted(seq, key=key):
        if n <= dist(key(x)):
            n += 1
            pruned.append(x)
    return pruned


def main(root, confirmed=False):
    keep = {}
    now = datetime.today()
    paths = list(root.glob('????-??-??-??????'))
    keep = prune(
        paths,
        lambda p: (now-datetime.strptime(p.name, '%Y-%m-%d-%H%M%S'))/timedelta(1),
        lambda x: 50*log10(1+sqrt(x))
    )
    delete = set(paths) - set(keep)
    for path in sorted(paths):
        print('x' if path in delete else ' ', path)
    print(f'Will delete ({len(delete)}/{len(paths)}):')
    if not confirmed and len(keep) < len(paths):
        answer = input('Proceed? [y]: ')
        if answer != 'y':
            return
    for path in sorted(delete):
        print(f'Deleting {path}...', end='', flush=True)
        subprocess.run(['rm', '-rf', str(path)])
        print(' Done.')


def cli():
    parser = ArgumentParser()
    arg = parser.add_argument
    arg('root', type=Path)
    arg('--confirmed', action='store_true')
    return vars(parser.parse_args())


if __name__ == '__main__':
    try:
        main(**cli())
    except KeyboardInterrupt:
        raise SystemExit(2)
