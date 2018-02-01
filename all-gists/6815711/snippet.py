# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from numpy import *
from pandas import *


from scipy.signal import argrelextrema

# <codecell>

# Download a list of all complete bacterial genomes from NCBI
import urllib
url = "http://www.ncbi.nlm.nih.gov/genomes/Genome2BE/genome2srv.cgi?action=download&orgn=&report=proks&status=Complete|&group=--%20All%20Bacteria%20--&subgroup=--%20All%20Bacteria%20--"
data = read_csv(urllib.urlopen(url), na_values='-', sep="\t")
no_refseq = isnull(data['Chromosomes/RefSeq'])
print "Without RefSeq: %i/%i" % (sum(no_refseq), len(no_refseq))
data = data[~no_refseq]

# <codecell>

# Take a peek at the table columns
data

# <codecell>

# Distribution of gene counts
data['Genes'].hist()

# <codecell>

# Distribution of genome sizes
data['Size (Mb)'].hist()

# <codecell>

# How many data do we have to download?
sum(data['Size (Mb)'])

# <codecell>

import os
try:
    os.mkdir('fasta')
except OSError:
    pass

try:
    os.mkdir('skew_plots')
except OSError:
    pass

# <codecell>

from Bio import Entrez, SeqIO
Entrez.email = ""     # Always tell NCBI who you are

# <codecell>

for index, row in data.iterrows():  
    for refseq in row['Chromosomes/RefSeq'].split(','):
        
        filename = "fasta/%s.fasta" % (refseq,)
        if os.path.exists(filename):
            continue
        print "%i/%i" % (index, len(data)) , refseq, row['#Organism/Name']
        handle = Entrez.efetch(db="nucleotide", id=refseq, rettype="fasta", retmode="text")
        seq = SeqIO.read(handle, 'fasta')
        output_handle = open(filename, "w")
        SeqIO.write(seq, output_handle, "fasta")
        output_handle.close()
    

# <codecell>


# <codecell>

def skew_increments(s):
    return [{'C': -1, 'A':0, 'T':0, 'G':1, 'N':0, 'S':0,'R':0, 'D':0, 'Y':0, 'K':0, 'M':0, 'W':0, 'B':0, 'V':0, 'H':0}[c] for c in s]
def gc_skew(s):
    return cumsum([0]+skew_increments(s))

# <codecell>

# Calculate and plot a simple example
seq = SeqIO.read(file("fasta/NC_017492.1.fasta"), "fasta").seq
skew = gc_skew(seq)[0::10000]
figure(figsize=(3,3))
plot(skew)
minima = argrelextrema(skew, less, order=10)[0]

# <codecell>


# <codecell>

# Iterate over each organism
for index, row in data.iterrows():
    # Each organism can have multiple chromosomes
    for refseq in row['Chromosomes/RefSeq'].split(','):
        filename = "fasta/%s.fasta" % (refseq,)
        if not os.path.exists(filename):
            continue
        image_name =  "%s(%s)" % (row['#Organism/Name'], refseq)
        image_name = "skew_plots/" + image_name.replace(" ", "_").replace(".", "").replace("/"," of ") + ".png"
        if os.path.exists(image_name):
            continue
        try:
            
            seq = SeqIO.read(file(filename), "fasta").seq
        except ValueError:
            print "error:", filename
            continue
        skew = gc_skew(seq)[0::10000]
        minima = argrelextrema(skew, less, order=10)[0]
        print "%i/%i" % (index, len(data)), refseq, row['#Organism/Name'], len(minima)
    
        figure(figsize=(3,3))
        plot(skew)
        
        title("%s\n%s" % (row['#Organism/Name'], refseq))
        savefig(image_name, bbox_inches='tight', pad_inches=0.5)

# <codecell>

1

# <codecell>


# <codecell>
