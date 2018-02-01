#!/usr/bin/env python

import datetime
import argparse
from tqdm import tqdm

def log(*args):
    msg = ' '.join(map(str, [datetime.datetime.now(), '>'] + list(args)))
    print(msg)
    with open('log.txt', 'at') as fd: fd.write(msg + '\n')

def main():
    psr = argparse.ArgumentParser()
    args = psr.parse_args()
    print('hello!', args)

if __name__ == '__main__': main()
