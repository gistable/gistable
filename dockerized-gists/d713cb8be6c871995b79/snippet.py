#!/usr/bin/env python
# encoding: utf-8

"""
Boyer Moore Demo
Inspired by https://www.youtube.com/watch?v=PHXAOKQk2dw
Copyright (C) 2015 Meng Zhuo <mengzhuo1203@gmail.com>
"""

def make_bad_match_table(pattern):

    length = len(pattern)
    table = {}
    for i, c in enumerate(pattern):
        if i == length-1 and not c in table:
            table[c] = length
        else:
            table[c] = length - i - 1

    return table


def boyer_moore(pattern, text):

    match_table = []
    pattern_length = len(pattern)
    text_length = len(text)
    if pattern_length > text_length:
        return match_table

    table = make_bad_match_table(pattern)
    index = pattern_length - 1
    pattern_index = pattern_length - 1

    while index < text_length:
        if pattern[pattern_index] == text[index]:
            if pattern_index == 0:
                match_table.append(index)
                pattern_index = pattern_length - 1
                index += (pattern_length * 2 - 1)
            else:
                pattern_index -= 1
                index -= 1
        else:
            index += table.get(text[index], pattern_length)
            pattern_index = pattern_length - 1

    return match_table

if __name__ == '__main__':

    pattern = "tooth"
    target = "trusthardtoothbrushestoothgood"
    print(boyer_moore(pattern, target))