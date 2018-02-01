from pysam import AlignmentFile
from pyfaidx import Fasta

def has_mismatch_in_interval(reference, bamfile, chrom, start, end):
    """
    Return whether there is a mismatch in the interval (start, end) in any read mapping to the given chromosome.

    reference -- a pyfaidx.Fasta object or something that behaves similarly
    """
    for column in bamfile.pileup(chrom, start, end):
        refbase = reference[chrom][column.pos:column.pos+1]
        for piledup in column.pileups:
            if piledup.indel != 0:  # Insertion is positive; deletion is negative
                # Ignore indels
                continue
            querybase = piledup.alignment.query_sequence[piledup.query_position]
            if refbase != querybase:
                # Mismatch
                return True
    return False


ref = Fasta('reference.fasta')
bamfile = AlignmentFile('mappedreads.bam')
has_mismatch_in_interval(ref, bamfile, 'scaffold17', 1000, 2000)
