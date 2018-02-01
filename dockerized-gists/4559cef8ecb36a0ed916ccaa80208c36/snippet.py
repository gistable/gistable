#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click


@click.command()
@click.option('--outfile', '-o')
@click.argument('src')
def fetch(outfile, src):
    import requests
    import os

    target_filename = src.split('/')[-1]
    req = requests.get(src, stream=True)

    if os.path.isdir(outfile):
        outfile = os.path.join(outfile, target_filename)

    with open(outfile, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    #print outfile

if __name__ == "__main__":
    fetch()