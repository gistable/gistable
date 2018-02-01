#!/usr/bin/env python
# quick script for demultiplexing reads from illumina fastq files
# Sean Davis <seandavi@gmail.com>
# 2012-06-29
#
import argparse
import Bio.SeqIO as SeqIO
from itertools import izip
import gzip
from string import maketrans
import subprocess

transtab = maketrans('ACGTN','TGCAN')

def revcomp(sequence,dropone=False):
    tmp=sequence[::-1].translate(transtab)
    if(dropone):
        tmp = tmp[1:]
    return(tmp)


def fileOpen(fname,mode='r'):
    if(fname.endswith('.gz')):
        if(mode.startswith('r')):
            return subprocess.Popen(['gunzip -c %s' % fname],stdout=subprocess.PIPE,shell=True).stdout
        if(mode.startswith('w')):
            return gzip.GzipFile(fname,'wb')
    else:
        return open(fname,'r')

parser = argparse.ArgumentParser(
    description="""Demultiplex fastq files based on an index.  

This script assumes that there are two OR three fastq files representing each cluster.  One of the  of the reads contains the index sequence.  The script matches the index (specified as the last argument to pull out reads from the non-index files to generate demultiplexed fastq files.""")
parser.add_argument('-1','--readFile1',required=True,
                    help="read1 filename")
parser.add_argument('-2','--readFile2',
                    help="read2 filename")
parser.add_argument('-i','--indexFile',required=True,
                    help="index Filename")
parser.add_argument('index',
                    help="The index")

opts = parser.parse_args()

print opts

indexString = revcomp(opts.index)
print indexString

ifile = SeqIO.parse(fileOpen(opts.indexFile),'fastq')
rfile1 = SeqIO.parse(fileOpen(opts.readFile1),'fastq')
ofile1 = fileOpen(opts.index + "_" + opts.readFile1,'wb')
if(opts.readFile2 is not None):
    ofile2 = fileOpen(opts.index + "_" + opts.readFile2,'wb')
    rfile2 = SeqIO.parse(fileOpen(opts.readFile2),'fastq')
    for (r1,r2,i) in izip(rfile1,rfile2,ifile):
        if(str(i.seq).startswith(indexString)):
            SeqIO.write(r1,ofile1,'fastq')
            SeqIO.write(r2,ofile2,'fastq')
else:
    for (r1,i) in izip(rfile1,ifile):
        if(str(i.seq).startswith(indexString)):
            SeqIO.write(r1,ofile1,'fastq')
