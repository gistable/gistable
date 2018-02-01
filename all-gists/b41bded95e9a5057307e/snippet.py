#!/usr/bin/env python3
from uuid import uuid4
import argparse

import pyperclip


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clipboard", action="store_true", help="store contents in system clipboard")
    parser.add_argument("-v", "--verbose", action="store_true", help="print uuid pasted to clipboard, if the flag is set")

    args = parser.parse_args()
    return vars(args)


def main():
    args = parse()

    uuid = str(uuid4())

    if args["clipboard"]:
        pyperclip.copy(uuid)
        if args["verbose"]:
            print("{} copied to clipboard".format(uuid))
    else:
        print(uuid)


if __name__ == "__main__":
    main()
