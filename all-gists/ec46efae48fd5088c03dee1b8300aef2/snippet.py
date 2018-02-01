#!usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
parser = argparse.ArgumentParser(description="""print vcf entry from secific positions""")
parser.add_argument("--version", action='version', version='1.0')
parser.add_argument('v', help='input vcf file')
parser.add_argument('p', help="""position you want to extract
                    no X or Y or MT chromosomes
                    Examples:
                        >>> "12:234534-0879854"
                        >>> "chr11:5754-69774"
                    """)
args = parser.parse_args()

c = args.p.split(':')[0]
target_chrom = int(c[3:]) if c.startswith('chr') else int(c)
start_pos, end_pos = args.p.split(':')[1].split('-')

with open(args.v, "r") as vcf_reader:
    for record in vcf_reader:
        if record.startswith('#'):
            continue
        chrom, pos = record.split('\t')[0:2]
        try:
            chrom = int(chrom)
        except ValueError:
            continue
        if chrom == target_chrom and \
            int(start_pos) <= int(pos) <= int(end_pos):
            print(record.strip())