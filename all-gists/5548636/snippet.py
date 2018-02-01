
aln_snps = {}
for aln in aln_files:
    recs = [f for f in SeqIO.parse(aln, 'fasta')]
    # strain names should be the last dash delimited element in fasta header
    strains = [rec.name.split('-')[-1] for rec in recs]
    # get a dictionary of strain names and sequences
    strain_seq = {rec.name.split('-')[-1]:''.join([nt for nt in rec.seq]) \
        for rec in recs}
    # get length of the MSA and check that all of the seq are the same length
    seq_len = 0
    len_check = {}
    for x in strain_seq:
        seq_len = len(strain_seq[x])
        len_check[seq_len] = 1
    if len(len_check) > 1:
        print 'Sequences in MSA', aln, 'not of the same length!'
        print [x for x in len_check]

    # list of snps
    snps = []
    for i in range(0, seq_len):
        nts = {}
        d = {}
        for strain in strains:
            nt = strain_seq[strain][i]
            nts[strain] = nt
            if nt not in d:
                d[nt] = 1
            else:
                d[nt] += 1
        
        if len(d) > 1:
            # add tuple containing:
            # i: index of SNP within sequence
            # d: nucleotide dictionary with counts for each nucleotide
            # nts: dictionary of strain and nucleotide at index i
            snps.append((i, d, nts))
    aln_snps[aln] = snps

