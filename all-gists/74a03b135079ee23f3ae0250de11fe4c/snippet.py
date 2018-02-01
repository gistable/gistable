#!/usr/bin/env python

# So.. developers who use spaces make more money than those who use tabs huh?
# https://stackoverflow.blog/2017/06/15/developers-use-spaces-make-money-use-tabs/

# We can automate that promotion!
from __future__ import print_function
import os
import fnmatch
from fileinput import FileInput

SUPREME_WHITESPACE = "    "
LESSER_WHITESPACE = "\t"

def instant_promotion(file_pattern):
    for path, dirs, files in os.walk(os.path.expanduser("~"), topdown=True):
        files = [os.path.join(path, filename) for filename in fnmatch.filter(files, file_pattern)]
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for l in FileInput(files, inplace=True, backup=".old"):
            print(l.replace(LESSER_WHITESPACE, SUPREME_WHITESPACE), end="")

exit("dont't run random code from the internet..")

instant_promotion("*.py")
