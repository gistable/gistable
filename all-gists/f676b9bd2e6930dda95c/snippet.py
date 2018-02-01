#script to accompany https://www.biostars.org/p/64078/

from Bio import Entrez
Entrez.email = "A.N.Other@example.com"

protein_accn_numbers = ["ABR17211.1", "XP_002864745.1", "AAT45004.1", "XP_003642916.1" ]
protein_gi_numbers = []

print "The Accession numbers for protein sequence provided:"
print protein_accn_numbers

#ESearch
print "\nBeginning the ESearch..."
# BE CAREFUL TO NOT ABUSE THE NCBI SYSTEM.
# see http://biopython.org/DIST/docs/tutorial/Tutorial.html#sec119 for information.
# For example, if searching with more than 100 records, you'd need to do this ESearch step
# on weekends or outside USA peak times.
for accn in protein_accn_numbers:
    esearch_handle = Entrez.esearch(db="protein", term=accn)
    esearch_result= Entrez.read(esearch_handle)
    esearch_handle.close()
    #print esearch_result
    #print esearch_result["IdList"][0]
    protein_gi_numbers.append(esearch_result["IdList"][0])
#print protein_gi_numbers

retrieved_mRNA_uids = []
#ELink
print "Beginning the ELink step..."
handle = Entrez.elink(dbfrom="protein", db="nuccore", LinkName="protein_nuccore_mrna", id=protein_gi_numbers)
result = Entrez.read(handle)
handle.close()
#print result
for each_record in result:
    mrna_id = each_record["LinkSetDb"][0]["Link"][0]["Id"]
    retrieved_mRNA_uids.append(mrna_id)
#print retrieved_mRNA_uids

#EPost
print "Beginning the EPost step..."
epost_handle = Entrez.epost(db="nuccore", id=",".join(retrieved_mRNA_uids))
epost_result = Entrez.read(epost_handle)
epost_handle.close()

webenv = epost_result["WebEnv"]
query_key = epost_result["QueryKey"]

#EFetch
print "Beginning the EFetch step..."
count = len(retrieved_mRNA_uids)
batch_size = 20
the_records = ""
for start in range(0, count, batch_size):
    end = min(count, start + batch_size)
    print("Fetching records %i thru %i..." % (start + 1, end))
    fetch_handle = Entrez.efetch(db="nuccore",
                                 rettype="fasta", retmode="text",
                                 retstart=start, retmax=batch_size,
                                 webenv=webenv,
                                 query_key=query_key)
    data = fetch_handle.read()
    fetch_handle.close()
    the_records = the_records + data
print the_records #for seeing how to save as file as get record blocks, see similar
# example at line 101, found under 'Update: Searching for citations using ELink,
# EPost and EFetch with history' of section '9.15.3 Searching for citations' ,
# at http://nbviewer.ipython.org/github/gumption/Using_Biopython_Entrez/blob/master/Biopython_Tutorial_and_Cookbook_Chapter_9.ipynb