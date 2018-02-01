"""
barcode_splitter.py

Barcode splitter for fastq sequencing files, that matches using Levenshtein
distance.

USAGE:

python barcode_splitter.py reads.fastq index_reads.fastq barcodes.txt

Takes three files: a raw reads file, a barcode index reads file, where each
barcode corresponds to a read in the raw file, and an catalog file in a
format similar to:

group1	TGACCA
group2	GCCAAT
group3	CAGATC

This program matches each index to the closest barcode, including mutations,
insertions, and deletions. It then splits the file according to those indices-
in this case, into group1.fastq, group2.fastq, and group3.fastq.
"""

import sys
import warnings
import itertools
import collections

from Bio import SeqIO


def levenshtein_distance(s1, s2):
    """
    Python version of Levenshtein distance for compatability. The third-party
    library is much faster and recommended. Taken from recipe at:
    http://code.activestate.com/recipes/576874-levenshtein-distance/
    """
    l1 = len(s1)
    l2 = len(s2)

    matrix = [range(l1 + 1)] * (l2 + 1)
    for zz in xrange(l2 + 1):
        matrix[zz] = range(zz, zz + l1 + 1)
    for zz in range(0, l2):
        for sz in range(0, l1):
            if s1[sz] == s2[zz]:
                matrix[zz + 1][sz + 1] = min(matrix[zz + 1][sz] + 1,
                                    matrix[zz][sz + 1] + 1, matrix[zz][sz])
            else:
                matrix[zz + 1][sz + 1] = min(matrix[zz + 1][sz] + 1,
                                    matrix[zz][sz + 1] + 1, matrix[zz][sz] + 1)
    return matrix[l2][l1]


try:
    import Levenshtein
    levenshtein_distance = Levenshtein.distance
except ImportError:
    warnings.warn("python-Levenshtein package not found. The package is " +
                  "recommended as it makes barcode splitting much faster. " +
                  "Using native Python Levenshtein distance function instead.")


class BarcodeIndex:
    """Represents a set of indices, with the ability to find the closest one"""
    def __init__(self, index_file, max_distance=3):
        self.cache = {}
        with open(index_file) as inf:
            for l in inf:
                if l.startswith("#") or l == "":
                    continue
                g, barcode = l.split("\t")
                self.cache[barcode] = g
        self.barcodes = self.cache.keys()
        self.groups = self.cache.values()
        self.max_distance = max_distance

    def find_barcode(self, barcode):
        """
        match barcode and return the group it's supposed to be in. If
        there is none within the Levenshtein distance given, or if there
        is a tie, return None
        """
        # if there's an exact match, return that
        exact = self.cache.get(barcode)
        if exact is not None:
            return exact

        # find the Levenshtein distance to each
        distances = [levenshtein_distance(barcode, b) for b in self.barcodes]
        best = min(distances)
        # check if there's a tie or the distance is too great:
        if best > self.max_distance or distances.count(best) > 1:
            return None
        # otherwise, return the best one, after caching it for future use
        ret = self.groups[distances.index(best)]
        self.cache[barcode] = ret
        return ret


def split_reads(read_file, barcode_file, index_file):
    """
    Given a fastq file of reads, a fastq file with corresponding barcodes,
    and a file with the barcode index. Create one fastq file for each group
    based on the closest matching barcode
    """
    index = BarcodeIndex(index_file)

    counts = collections.defaultdict(int)

    # one output for each group
    outfs = dict([(g, open(g + ".fastq", "w"))
                    for g in index.groups + ["Unassigned"]])

    with open(read_file) as read_inf, open(barcode_file) as barcode_inf:
        for r, b in itertools.izip(SeqIO.parse(read_inf, "fastq"),
                                   SeqIO.parse(barcode_inf, "fastq")):
            group = index.find_barcode(str(b.seq))
            group = group if group != None else "Unassigned"
            SeqIO.write([r], outfs[group], "fastq")
            counts[group] += 1

        for k, v in sorted(counts.items(), key=lambda t: t[0] == "Unassigned"):
            print k, v

    for o in outfs.values():
        o.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "USAGE: python barcode_splitter.py reads.fastq index.fastq",
        print "barcodes.txt"
        sys.exit(1)
    [read_file, barcode_file, index_file] = sys.argv[1:]
    split_reads(read_file, barcode_file, index_file)
