# Code written by brentp in response to BioStars question:
# http://www.biostars.org/post/show/6544/

import random
import sys

def write_random_records(fqa, fqb, N=100000):
    """ get N random headers from a fastq file without reading the
    whole thing into memory"""
    records = sum(1 for _ in open(fqa)) / 4
    rand_records = sorted([random.randint(0, records - 1) for _ in xrange(N)])

    fha, fhb = open(fqa),  open(fqb)
    suba, subb = open(fqa + ".subset", "w"), open(fqb + ".subset", "w")
    rec_no = - 1
    for rr in rand_records:

        while rec_no < rr:
            rec_no += 1       
            for i in range(4): fha.readline()
            for i in range(4): fhb.readline()
        for i in range(4):
            suba.write(fha.readline())
            subb.write(fhb.readline())
        rec_no += 1 # (thanks @anderwo)

    print >>sys.stderr, "wrote to %s, %s" % (suba.name, subb.name)

if __name__ == "__main__":
    N = int(sys.argv[3])
    write_random_records(sys.argv[1], sys.argv[2], N)