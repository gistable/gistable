#!/usr/bin/env python
# encoding: utf-8
"""
bed_from_genbank.py

grab the gene records from a genbank file (edit for other record types).

- requires:  biopython

"""

from Bio import SeqIO

import pdb

def main():
    outf = open('test/annotation/vitis_vinifera.bed', 'w')
    header = """track name=vitVinGenes description="V. vinifera cpdna genes" itemRgb=On\n"""
    outf.write(header)
    for record in SeqIO.parse(open("test/annotation/vitis_vinifera.gb", "rU"), "genbank") :
        for feature in record.features:
            if feature.type == 'gene':
                start = feature.location.start.position
                stop = feature.location.end.position
                try:
                    name = feature.qualifiers['gene'][0]
                except:
                    # some features only have a locus tag
                    name = feature.qualifiers['locus_tag'][0]
                if feature.strand < 0:
                    strand = "-"
                else:
                    strand = "+"
                bed_line = "cpdna\t{0}\t{1}\t{2}\t1000\t{3}\t{0}\t{1}\t65,105,225\n".format(start, stop, name, strand)
                outf.write(bed_line)
    outf.close()


if __name__ == '__main__':
    main()
