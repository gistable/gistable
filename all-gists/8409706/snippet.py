import argparse
import textwrap
import os
import sys
from datetime import timedelta, datetime


# function for reading a multifasta file
# returns a dictionary with sequence headers and nucleotide sequences
def get_seqs_from_fasta(filepath):
    header_seq = {}
    with open(filepath, 'r') as f:
        seqs = []
        header = ''
        for line in f:
            line = line.rstrip()
            if '>' in line:
                if header == '':
                    header = line.replace('>','')
                else:
                    header_seq[header] = ''.join(seqs)
                    seqs = []
                    header = line.replace('>','')
            else:
                seqs.append(line)
        header_seq[header] = ''.join(seqs)
    return header_seq


def get_strain_names(aln_snps):
    alns = [aln for aln in aln_snps]
    # get strain names from first aln in alns list
    strains = set(aln_snps[alns[0]]['strains'])
    # all other aln files should have this same list of strains
    for aln in alns[1:]:
        curr_aln_strains = set(aln_snps[aln]['strains'])
        # get new strain names in either the current set of strain names
        # or the set of strain names from the first multifasta
        if len(strains ^ curr_aln_strains) > 0:
            # show which MSA files don't match up
            print 'Error: Difference in the strains present in {0} compared to {1} where the strain names {2} are not found in both MSA files'.format(alns[0], aln, strains ^ curr_aln_strains)
            # don't return a list of strains
            return None
    # assuming that each list of strains for each MSA are in the same order
    return aln_snps[alns[0]]['strains']


# function to get the SNPs between all sequences within an MSA
# returns a dictionary with 
# - the MSA sequence length
# - list of alphabetically sorted strain names
# - a list of SNPs
#   - index
#   - nt frequency
#   - nt character (A, G, C, T, -, etc)
def get_snps_from_aln(aln_path):
    # get the strain-sequence dictionary for the MSA
    # strain name is the fasta sequence header
    strain_seq = get_seqs_from_fasta(aln_path)

    # get a list of the strain names from the strain-sequence dictionary
    strains = [strain for strain in strain_seq]
    # sort alphabetically
    strains.sort()

    # get length of the MSA and check that all of the seq are the same length
    seq_len = 0
    len_check = set()
    for x in strain_seq:
        seq_len = len(strain_seq[x])
        len_check.add(seq_len)
    if len(len_check) > 1:
        print 'Sequences in MSA', aln_path, 'not of the same length!'
        print [x for x in len_check]

    # get the list of SNPs
    snps = []
    for nt_index in range(0, seq_len):
        # get list of nucleotides at the current sequence position
        nts = [strain_seq[strain][nt_index] for strain in strains]
        # check if there is a SNP at this position
        if len(set(nts)) == 1:
            # if there isn't then continue onto the next position
            continue

        # get the nucleotide frequency
        nt_counts = {}
        for nt in nts:
            if nt not in nt_counts:
                nt_counts[nt] = 1
            else:
                nt_counts[nt] += 1
        
        # add a small dictionary containing:
        # nt_index: index of SNP within sequence
        # nt_counts: nucleotide dictionary with counts for each nucleotide
        # nts: list of nucleotide at index i
        snps.append(
            {'index':nt_index, 
            'nt_counts':nt_counts, 
            'nts':nts})
    return {'seq_len':seq_len, 'strains':strains, 'snps':snps}


# function to get SNPs from MSAs in parallel using Parallel Python (pp)
def get_snps_pp(aln_files):
    # create a Parallel Python job server
    # job_server = pp.Server()
    
    # store jobs in a dictionary with
    # key:   MSA file
    # value: job object (contains result)
    jobs = {}
    for aln_path in aln_files:
        # create a job and submit it to the job server
        # need to specify main function and the functions, arguments and modules it depends upon
        # job = job_server.submit(get_snps_from_aln, (aln_path,), (get_seqs_from_fasta,))
        # add the job to the dictionary of jobs
        # jobs[aln_path]  = job
        jobs[aln_path] = get_snps_from_aln(aln_path)
        # print 'got snps for', aln_path
    return jobs
    # wait for all of the jobs to finish
    # job_server.wait()
    # job_server.print_stats()
    # collect and return the job results as a dictionary with
    # key:   MSA file 
    # value: SNPs result dictionary
    # ret = {}
    # for x in jobs:
    #     job = jobs[x]
    #     result = job()
    #     ret[x] = result
        # print x, result, job
    # return ret
    # return {aln_path:jobs[aln_path]() for aln_path in jobs}


# function to write a simple SNP report showing the number of SNPs, % SNPs/len of MSA for each MSA, etc
def write_snp_report(snp_report_path, aln_snps, strains):
    with open(snp_report_path, 'w') as f:
        f.write('\t'.join(['aln','% SNPs', '# SNPs', '% Gaps','Gaps', '% Non-gap SNPs', 'Non-gap SNPs', 'MSA len']) + '\n')
        for aln_file in aln_snps:
            num_snps = len(aln_snps[aln_file]['snps'])
            num_gaps = len([snp for snp in aln_snps[aln_file]['snps'] if '-' in snp['nt_counts']])
            msa_len = float(aln_snps[aln_file]['seq_len'])
            perc_snps = num_snps / msa_len * 100.0
            perc_gaps = num_gaps / msa_len * 100.0
            non_gap_snps = num_snps - num_gaps
            perc_non_gap_snps = non_gap_snps / msa_len * 100.0
            f.write('\t'.join([
                aln_file, 
                str(perc_snps),  
                str(num_snps), 
                str(perc_gaps),
                str(num_gaps),
                str(perc_non_gap_snps),
                str(non_gap_snps),
                str(msa_len)]))
            f.write('\n')


# write a SNP table 
def write_snp_table(snp_table_path, aln_snps, strains, write_binary):
    nt_types = "AGCTN-"
    with open(snp_table_path, "w") as f:
        f.write("\t".join(['MSA', "SNP Location", "Has Dash?", "Has N?", "\t".join(["No. of " + nt for nt in nt_types]), "\t".join(strains)]))
        f.write("\n")
        for aln in aln_snps:
            strains = aln_snps[aln]['strains']
            for snp_dict in aln_snps[aln]['snps']:
                snp_location = snp_dict['index']
                nt_counts = snp_dict['nt_counts']
                strain_snps = snp_dict['nts']
                nt_count_list = [str(nt_counts[nt]) if nt in nt_counts else "0" for nt in nt_types]
                has_dash = "TRUE" if "-" in nt_counts else "FALSE"
                has_N = "TRUE" if "N" in nt_counts else "FALSE"
                if write_binary:
                    for nt in nt_counts:
                        binary_nts = ["1" if snp_nt == nt else "0" for snp_nt in strain_snps]
                        f.write("\t".join([aln, str(snp_location), nt, has_dash, has_N, "\t".join(nt_count_list), "\t".join(binary_nts)]))
                        f.write("\n")
                else:
                    f.write("\t".join([aln, str(snp_location), has_dash, has_N, "\t".join(nt_count_list), "\t".join(strain_snps)]))
                    f.write("\n")

# write a SNP table 
def write_genomefisher_snp_table(snp_table_path, aln_snps, strains):
    nt_types = "AGCTN-"
    with open(snp_table_path, "w") as f:
        f.write("\t".join(['SNP', "\t".join(strains)]))
        f.write("\n")
        for aln in aln_snps:
            strains = aln_snps[aln]['strains']
            for snp_dict in aln_snps[aln]['snps']:
                snp_location = snp_dict['index']
                nt_counts = snp_dict['nt_counts']
                strain_snps = snp_dict['nts']
                for nt in nt_counts:
                    binary_nts = ["1" if snp_nt == nt else "0" for snp_nt in strain_snps]
                    f.write("\t".join(['_'.join([aln, str(snp_location), nt]), "\t".join(binary_nts)]))
                    f.write("\n")

def get_concatenated_snp_seq(aln_snps, strains):
    # initialize dictionary to store SNP sequences
    # key:   strain name
    # value: list of concatenated SNP sequences for each MSA file
    strain_snp_seq = {strain:[] for strain in strains}
    
    for aln in aln_snps:
        for i in range(0, len(strains)):
            strain = strains[i]
            strain_nts = ''.join([snp_dict['nts'][i] \
                for snp_dict in aln_snps[aln]['snps'] \
                # could have one or more conditions here 
                # e.g. not allowing positions with dashes or positions that are not 2-fold snps 
                #if len(snp_dict['nt_counts']) != 2: 
                #    continue
                # or only grab SNPs that are not unique (found in 2 or more strains)

                # Here only one condition is used to filter SNPs
                # don't add gap sites to concatenated SNP sequences
                if '-' not in snp_dict['nt_counts']])

            strain_snp_seq[strain].append(strain_nts)

    # need to concatenate list of SNP sequences for each strain
    strain_cat_snp_seq = {strain:''.join(strain_snp_seq[strain]) for strain in strains}
    return strain_cat_snp_seq


def write_concatenated_snp_seq_fasta(concat_fasta_path, aln_snps, strains):
    strain_cat_snp_seq = get_concatenated_snp_seq(aln_snps, strains)
    with open(concat_fasta_path, 'w') as f:
        for strain in strains:
            f.write('>{0}\n'.format(strain))
            f.write('{0}\n'.format(strain_cat_snp_seq[strain]))




prog_desc = '''
    Parse SNPs from multiple sequence alignments (MSAs)
    ---------------------------------------------------

    Parse SNPs from MSAs in multifasta format files where all multifasta files 
    have the same strains and the same number of strains. The strain name 
    identifiers must be the same.

    Example Usage:

        $ python parseSNPs.py -c snps.fasta -b bin_snps.txt -g genomefisher_snps.txt -t snps.txt -r report.txt MSAs_dir/*.fasta

    Multifasta format:

        Multifasta file 1:

            >strain_A
            ...
            >strain_B
            ...
            >strain_C 
            ...

        Multifasta file 2:

            >strain_A
            ...
            >strain_B
            ...
            >strain_C 
            ...

    '''

parser = argparse.ArgumentParser(prog='parseSNPs',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent(prog_desc))
parser.add_argument('-c', '--concat_snp_path', help='Concatenated SNPs multifasta save path')
parser.add_argument('-t', '--snp_table_path', help='SNP table save path')
parser.add_argument('-b', '--bin_snp_table_path', help='Binarized SNP table save path. (GenomeFisher compatible with some modification)')
parser.add_argument('-g', '--genomefisher_snp_table_path', help='GenomeFisher compatible binarized SNP save path')
parser.add_argument('-r', '--snp_report_path', help='SNP report save path')
parser.add_argument('multifastas', metavar='F', nargs='+', help='Multifasta alignment file path')


args = parser.parse_args()
print 'No. of Multifastas:', len(args.multifastas)

if args.concat_snp_path is None and args.bin_snp_table_path is None and args.snp_table_path is None and args.snp_report_path is None and args.genomefisher_snp_table_path is None:
    print 'No files specified to be saved. Please specify concatenated SNP multifasta save path, binarized SNPs table save path, and/or SNP report save path.'
else:
    start_dt = datetime.now()
    print '[{0}]: SNP parsing started.'.format(start_dt.strftime('%c'))


    # run pp function to get the SNPs for each MSA within a specified directory
    aln_snps = get_snps_pp(args.multifastas)

    print '[{0}]: SNPs parsed from multifasta files'.format(datetime.now().strftime('%c'))

    strains = get_strain_names(aln_snps)

    print '[{0}]: Strain names retrieved'.format(datetime.now().strftime('%c'))

    if args.snp_report_path is not None:
        # write a SNP report
        write_snp_report(args.snp_report_path, aln_snps, strains)
        print '[{0}]: SNP report written to {1}'.format(datetime.now().strftime('%c'), args.snp_report_path)

    if args.snp_table_path is not None:
        # write the SNP table
        write_snp_table(args.snp_table_path, aln_snps, strains, False)
        print '[{0}]: SNP table written to {1}'.format(datetime.now().strftime('%c'), args.snp_table_path)


    if args.bin_snp_table_path is not None:
        # write the binarized SNP table
        write_snp_table(args.bin_snp_table_path, aln_snps, strains, True)
        print '[{0}]: binarized SNP table written to {1}'.format(datetime.now().strftime('%c'), args.bin_snp_table_path)

    if args.genomefisher_snp_table_path is not None:
        # write the binarized SNP table compatible with GenomeFisher
        write_genomefisher_snp_table(args.genomefisher_snp_table_path, aln_snps, strains)
        print '[{0}]: GenomeFisher compatible binarized SNP table written to {1}'.format(datetime.now().strftime('%c'), args.genomefisher_snp_table_path)

    if args.concat_snp_path is not None:
        write_concatenated_snp_seq_fasta(args.concat_snp_path, aln_snps, strains)
        print '[{0}]: concatenated SNP multifasta file written to {1}'.format(datetime.now().strftime('%c'), args.concat_snp_path)

    completed_dt = datetime.now()
    print '[{0}]: SNP parsing complete'.format(completed_dt.strftime('%c'))
    print 'Runtime: {0}'.format(completed_dt - start_dt)
