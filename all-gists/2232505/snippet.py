#!/usr/bin/env python
# encoding: utf-8

import sys
import argparse

def interface():
    parser = argparse.ArgumentParser()

    parser.add_argument('--rm-short-reads',
                      type=int,
                      help='Minimum number of base pairs \
                      either R1 or R2 read must be.') 

    # add additional trimming/filtering functionality as needed. 

    parser.add_argument('LEFT_INPUT',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        nargs='?',
                        help='R1 reads.')

    parser.add_argument('RIGHT_INPUT',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        nargs='?',
                        help='R2 reads.')

    parser.add_argument('INTERLEAVED_OUTPUT',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        nargs='?',
                        help='Alignment file.')

    args = parser.parse_args()
    return args


def process_reads(args):
    
    left = args.LEFT_INPUT
    right = args.RIGHT_INPUT
    fout = args.INTERLEAVED_OUTPUT

    # USING A WHILE LOOP MAKES THIS SUPER FAST
    # Details here: 
    #   http://effbot.org/zone/readline-performance.htm
    
    while 1: 

        # process the first file
        left_id = left.readline()
        if not left_id: break
        left_seq = left.readline()
        left_plus = left.readline()
        left_quals = left.readline()

        # process the second file
        right_id = right.readline()
        right_seq = right.readline()
        right_plus = right.readline()
        right_quals = right.readline()

        if len(left_seq.strip()) <= args.rm_short_reads:
            continue

        if len(right_seq.strip()) <= args.rm_short_reads:
            continue

        # write output
        fout.write(left_id)
        fout.write(left_seq)
        fout.write(left_plus)
        fout.write(left_quals)

        fout.write(right_id)
        fout.write(right_seq)
        fout.write(right_plus)
        fout.write(right_quals)

    left.close()
    right.close()
    fout.close()
    return 0

if __name__ == '__main__':
    args = interface()
    process_reads(args)