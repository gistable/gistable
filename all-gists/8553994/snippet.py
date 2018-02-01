# Mitchell Stanton-Cook
# m.stantoncook@gmail.com
# github.com/mscook

import glob

"""
(> XXXXX       47,065 unmapped pairs
(> XXXXX       19,785 unmapped reads
(> XXXXX    5,098,912 reads/pairs with alignments
(> XXXXX      239,986 hit multiple locations (discarded)
(> XXXXX    3,904,585 pairs kept
(> XXXXX      954,341 reads kept
(> XXXXX      456.289 average depth of coverage, ambiguous
(> XXXXX      339.786 average depth of coverage, unambiguous

(> XXXXX      221.503 mean fragment size
(> XXXXX       84.467 s.d. fragment size

(> XXXXX           44 SNPs called
(> XXXXX           25 deletions called
(> XXXXX           10 insertions called
(> XXXXX        0.000 expected number of false SNP/indel calls
"""

inf = glob.glob("*/")

skip = ['pbs/', 'nway-SNPs_INDELS-comparison/']

header = ("StrainID,Unmapped pairs,Unmapped reads,Alignments,"+
          "Hit multiple locations (discarded),Pairs kept,Reads kept,"+
          "Average depth of coverage (ambiguous),"+
          "Average depth of coverage (unambiguous),"+
          "Insert mean,Insert s.d,SNPs called,"+
          "Deletions called,Insertions called,Expected false calls")

print header
for f in inf:
    if f not in skip:
        with open(f+'consensus_log.txt') as fin:
            cur = ''
            for line in fin:
                if line.startswith('(>'):
                    cur = cur+","+line.split(f[:-1])[-1].lstrip().split(' ')[0].replace(',', '')
            print f[:-1]+cur
