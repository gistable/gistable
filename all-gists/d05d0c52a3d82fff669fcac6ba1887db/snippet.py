#!/usr/bin/env python3
from gmusicapi import Musicmanager # pip install gmusicapi
from glob import glob
from argparse import ArgumentParser

m = Musicmanager()
if not m.login():
    m.perform_oauth()
    m.login()

def main():
    parser = ArgumentParser()
    parser.add_argument("files", nargs="+", help="Files to upload")
    args = parser.parse_args()
    for file in args.files:
        if '*' in file:
            for subfile in glob(file):
                print("Starting on {}...".format(subfile), end="\r")
                m.upload(subfile)
                print("Completed {}     ".format(subfile))
        else:
            print("Starting on {}...".format(file), end="\r")
            m.upload(file)
            print("Completed {}     ".format(file))

if __name__ == "__main__":
    main()