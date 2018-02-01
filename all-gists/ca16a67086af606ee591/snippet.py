#!/bin/env python                                                                                                                                                                                         

import fileinput

idx = 1
samples = []
for line in fileinput.input():
    if line.startswith("##"):
        continue
    if line.startswith("#CHROM"):
        samples = line.rstrip().split("\t")[9:]
    else:
        fields = line.rstrip().split("\t")
        chrom = fields[0]
        start = fields[1]
        end = fields[7].split(";")[0].split("=")[1]
        for i in range(len(samples)):
            sample_fields = fields[9+i].split(":")
            cn = sample_fields[1]
            filt = sample_fields[len(sample_fields)-1]
            if filt != "LowQual" and  cn != "2":
                print "\t".join([samples[i], samples[i], chrom, start, end, cn, "0", "0"])
    idx = idx + 1
