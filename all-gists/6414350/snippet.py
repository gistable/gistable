"""
gtf_flux_fix.py

Author: Ben Langmead (langmea@cs.jhu.edu)
Date: Sept 2, 2013

Remove GTF records for sequence IDs that don't appear in any of the specified
FASTA files.  Move the transcript_id attribute into the first attribute
position.  Output transformed GTF to stdout.
"""

import sys
import string
import argparse

parser = argparse.ArgumentParser(\
    description='Fix GTF file in preparation for Flux Simulator')

parser.add_argument(\
    '--gtf', metavar='PATH', type=str, required=True, nargs='+',
    help='Path to GTF file to fix')
parser.add_argument(\
    '--fasta', metavar='PATH', type=str, required=True, nargs='+',
    help='Path to corresponding FASTA files')

args = parser.parse_args()

fasta_names = set()

# Parse out all the sequence names
for fafn in args.fasta:
    print >> sys.stderr, "Parsing fasta: '%s'" % fafn
    with open(fafn, 'r') as fafh:
        for line in fafh:
            if line[0] == '>':
                nm = line[1:].rstrip()
                if ' ' in nm: nm = nm[:nm.index(' ')]
                fasta_names.add(nm)

print >> sys.stderr, "Fasta names:\n" + str(fasta_names) + "\n"

def transformAttr(attr):
    toks = string.split(attr)
    idx = toks.index("transcript_id")
    lab, val = toks[idx], toks[idx+1]
    del toks[idx]
    del toks[idx]
    toks.insert(0, val)
    toks.insert(0, lab)
    return ' '.join(toks)

unk_fasta_names = set()

# Now parse and transform the GTF
for gtffn in args.gtf:
    print >> sys.stderr, "Parsing gtf: '%s'" % gtffn
    with open(gtffn, 'r') as gtffh:
        for line in gtffh:
            toks = string.split(line.rstrip(), '\t')
            assert len(toks) == 9
            refid, source, feat, st, en, score, strand, frame, attr = toks
            if refid not in fasta_names:
                unk_fasta_names.add(refid)
                continue
            print '\t'.join([refid, source, feat, st, en, score, strand, frame, transformAttr(attr)])

print >> sys.stderr, "Removed at least 1 gtf record with each of the following reference ids:\n" + str(unk_fasta_names) + "\n"
