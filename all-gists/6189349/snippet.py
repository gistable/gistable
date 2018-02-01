#! /usr/bin/env/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys


def main():

    # Ask a question
    question = get_input("\nWhat do you have to say for yourself? ")
    # Send back user input
    print(question)
    sys.exit(0)

if __name__ == "__main__":
    # Support Python 2 and 3 input
    # Default to Python 3's input()
    get_input = input

    # If this is Python 2, use raw_input()
    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input

    main()
