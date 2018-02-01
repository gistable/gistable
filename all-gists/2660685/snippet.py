# requires biopython
# run like:
#   genbank_to_tbl.py "my organism name" "my strain ID" "ncbi project id" < my_sequence.gbk
#   writes seq.fsa, seq.tbl as output

import sys
from copy import copy
from Bio import SeqIO

def find_gene_entry(features, locus_tag):
    for f in features:
        if f.type == 'gene':
            if f.qualifiers['locus_tag'][0] == locus_tag:
                return f
    print locus_tag
    raise ValueError

coding = ['CDS', 'tRNA', 'rRNA']

def go():
    seqid = 0
    fasta_fh = open("seq.fsa", "w")
    feature_fh = open("seq.tbl", "w")
    allowed_tags = ['locus_tag', 'gene', 'product', 'pseudo', 'protein_id', 'gene_desc', 'old_locus_tag']
    records = list(SeqIO.parse(sys.stdin, "genbank"))

    for rec in records:
        for f in rec.features:
            if f.type in coding and 'gene' in f.qualifiers:
                print f.qualifiers['locus_tag'][0]

                f2 = find_gene_entry(rec.features, f.qualifiers['locus_tag'][0])
                f2.qualifiers['gene'] = f.qualifiers['gene']

                del f.qualifiers['gene']

    for rec in records:
        seqid += 1

        if len(rec) <= 200:
            print >>sys.stderr, "skipping small contig %s" % (rec.id,)
            continue

#        rec.id = rec.name = "%s%08d" % (sys.argv[4], seqid,)

        circular = rec.annotations.get('molecule', 'linear')
        rec.description = "[organism=%s] [strain=%s] [topology=%s] [molecule=DNA] [tech=wgs] [gcode=11]" % (sys.argv[1], sys.argv[2], circular)
        SeqIO.write([rec], fasta_fh, "fasta")

        print >>feature_fh, ">Feature %s" % (rec.name,)
        for f in rec.features:
            if f.strand == 1:
                print >>feature_fh, "%d\t%d\t%s" % (f.location.nofuzzy_start + 1, f.location.nofuzzy_end, f.type)
            else:
                print >>feature_fh, "%d\t%d\t%s" % (f.location.nofuzzy_end, f.location.nofuzzy_start + 1, f.type)

            if f.type == 'CDS' and 'product' not in f.qualifiers:
                f.qualifiers['product'] = ['hypothetical protein']

            if f.type == 'CDS':
                f.qualifiers['protein_id'] = ["gnl|ProjectID_%s|%s" % (sys.argv[3], f.qualifiers['locus_tag'][0])]

            if f.type in coding:
                del f.qualifiers['locus_tag']

            for key, vals in f.qualifiers.iteritems():
                my_allowed_tags = copy(allowed_tags)
                if 'pseudo' in f.qualifiers:
                    my_allowed_tags.append('note')

                if key not in my_allowed_tags:
                    continue

                for v in vals:
                    if len(v) or key == 'pseudo':
                        print >>feature_fh, "\t\t\t%s\t%s" % (key, v)


go()
