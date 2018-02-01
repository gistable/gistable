#!bin/python

import gzip
import io
import sys
import os

# This file will generate a bedfile of the masked regions a fasta file.

# STDIN or arguments
if len(sys.argv) > 1:

    # Check file type
    if sys.argv[1].endswith(".fa.gz"):
        input_fasta = io.TextIOWrapper(io.BufferedReader(gzip.open(sys.argv[1])))
    elif sys.argv[1].endswith(".fa") or sys.argv[1].endswith(".txt"):
        input_fasta = file(sys.argv[1],'r')
    else:
        raise Exception("Unsupported File Type")
else:
    print """
    \tUsage:\n\t\tgenerate_masked_ranges.py <fasta file | .fa or .fa.gz> <chrome find> <chrome replace>
    
    \t\t'Chrome find' and 'chrome replace' are used to find and replace the name of a chromsome. For example,
    \t\treplacing CHROMSOME_I with chr1 can be accomplished by using the command as follows:

    \t\t\tpython generate_masked_ranges.py my_fasta.fa CHROMSOME_ chr

    \t\tOutput is to stdout
    """
    raise SystemExit


n, state = 0, 0 # line, character, state (0=Out of gap; 1=In Gap)
chrom, start, end = None, None, None

with input_fasta as f:
    for line in f:
        line = line.replace("\n","")
        if line.startswith(">"):
            # Print end range
            if state == 1:
                print '\t'.join([chrom ,str(start), str(n)])
                start, end, state  = 0, 0, 0
            n = 0 # Reset character
            chrom = line.split(" ")[0].replace(">","")
            # If user specifies, replace chromosome as well
            if len(sys.argv) > 2:
                chrom = chrom.replace(sys.argv[2],sys.argv[3])
        else:
            for char in line:
                if state == 0 and char == "N":
                    state = 1
                    start = n
                elif state == 1 and char != "N":
                    state = 0
                    end = n
                    print '\t'.join([chrom ,str(start), str(end)])
                else:
                    pass

                n += 1 # First base is 0 in bed format.

# Print mask close if on the last chromosome.
if state == 1:
            print '\t'.join([chrom ,str(start), str(n)])
            start, end, state  = 0, 0, 0
