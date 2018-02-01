#!/usr/bin/python

from Bio import SeqIO
import sys

readDict = dict()

with open(sys.argv[1],"rb") as r1:
	for record in SeqIO.parse(r1,'fastq'):
		readDict[record.id] = dict()
		readDict[record.id]["r1"] = [record.id,record.description,record.seq,record.quality]
		readDict[record.id]["r2"] = None

with open(sys.argv[2],"rb") as r2:
	for record in SeqIO.parse(r2,'fastq'):
		if readDict.has_key(record.id):
			readDict[record.id]["r2"] = [record.id,record.description,record.seq,record.quality]
		else:
			readDict[record.id] = dict()
			readDict[record.id]["r1"] = None
			readDict[record.id]["r2"] = [record.id,record.description,record.seq,record.quality]
			

with open(sys.argv[3]+".r1.fastq","w") as pe1, open(sys.argv[3]+".r2.fastq","w") as pe2, open(sys.argv[3]+".se.fastq","w") as se:
	for key in readDict:
		if readDict[key]["r1"] == None:
			se.write("@"+readDict[key]["r2"][0]+" "+readDict[key]["r2"][1]+"\n"+readDict[key]["r2"][2]+"\n+\n"+readDict[key]["r2"][4])
		elif readDict[key]["r2"] == None:
			se.write("@"+readDict[key]["r1"][0]+" "+readDict[key]["r1"][1]+"\n"+readDict[key]["r1"][2]+"\n+\n"+readDict[key]["r1"][4])
		else:
			pe1.write("@"+readDict[key]["r1"][0]+" "+readDict[key]["r1"][1]+"\n"+readDict[key]["r1"][2]+"\n+\n"+readDict[key]["r1"][4])
			pe2.write("@"+readDict[key]["r2"][0]+" "+readDict[key]["r2"][1]+"\n"+readDict[key]["r2"][2]+"\n+\n"+readDict[key]["r2"][4])
