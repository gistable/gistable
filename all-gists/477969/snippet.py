"""                                                                                 
%prog some.fasta wanted-list.txt                                                    
"""                                                                                 
from Bio import SeqIO                                                               
import sys                                                                          
                                                                                    
wanted = [line.strip() for line in open(sys.argv[2])]                               
seqiter = SeqIO.parse(open(sys.argv[1]), 'fasta')                                    
SeqIO.write((seq for seq in seqiter if seq.id in wanted), sys.stdout, "fasta")