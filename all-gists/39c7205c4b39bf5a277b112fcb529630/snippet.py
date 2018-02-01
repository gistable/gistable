from argparse import ArgumentParser
from subprocess import Popen, PIPE
from hashlib import sha1
from os import path, walk
import re
import os
from sys import stderr


def extension_dir():
    return Popen(["php-config", "--extension-dir"], stdout=PIPE).stdout.read().decode().strip()


def hash_files():
    for root, dirs, files in walk(extension_dir()):
        for file in files:
            file = path.join(root, file)
            yield file, hash_file(file)


def hash_file(file):
    with open(file, "rb") as data:
        return sha1(data.read()).hexdigest()


def check_hashes(hashes):
    with open(hashes) as file:
        for expected_path, expected_hash in (line.strip().split(", ") for line in file):
            if hash_file(expected_path) != expected_hash:
                yield expected_path


def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--list", help="List hashes, save these to a file which you will use later", action="store_true")
    group.add_argument("-c", "--check", help="Check that all hashes are equal in the given file")
    args = parser.parse_args()

    if args.list:
        for full_path, file in hash_files():
            print("{}, {}".format(full_path, file))
        else:
            print("[!] Unable to find any extensions", file=stderr)

    if args.check:
        for expected_path in check_hashes(args.check):
            print("[!] Potentially malicious extension detected: {}".format(expected_path), file=stderr)
        else:
            print("[+] No changes detected")


if __name__ == "__main__":
    main()
