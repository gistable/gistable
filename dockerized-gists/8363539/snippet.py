import urllib2
response = urllib2.urlopen('http://www.uniprot.org/uniprot/Q96EB6.fasta')
fastaEntry = response.read()
print fastaEntry