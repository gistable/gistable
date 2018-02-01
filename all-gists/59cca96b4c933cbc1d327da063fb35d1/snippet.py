#!/usr/bin/python
from __future__ import print_function  
import csv
import sys


#First and last channel for each ROI. Edit as needed:
rois={'Tc99m': [37, 52],
'Ba133': [107,139], 
'I131': [113,121],
'Ir192': [144,174],
'Cs137': [200,237],
'Co60': [350,462]}

#For file naming - rename as appropriate:
organisation='NRPA'
detector='NAI8l'


nucs=['Tc99m','Ba133','I131','Ir192','Cs137','Co60']
# needed as the sorting of the keys in a dict cannot be granted

numoffields=1051 # expected number of fields in CSV-file
roifrom=1
roito=1024
offsetcol=22 # number of columns before ch1

if(len(sys.argv)>1):
   file=sys.argv[1]
else: # No command line arguments
  print("Usage:")
  print(sys.argv[0]+" <filename>")
  quit()

reader = csv.reader(open(file, "rb"))
i=0
outfile=''
f=''
for row in reader:
  i=i+1
  if(i<4):
    if (i>1) and (len(row) !=numoffields):
      print("Invalid number of fields in csv")
      quit() 
  else:
   if outfile=='':
      outfile=organisation+'-'+detector+'-'+row[1].replace('/','-')+'-'+row[2].replace(':','')+'-'+'S.csv'
      f=open(outfile,'w')   
   line=list((row[1],row[2],"1",row[11],row[10]))
   for nuc in nucs:
      # print rois[nuc]
      ROI=row[rois[nuc][0]+offsetcol:rois[nuc][1]+offsetcol+1]
      # print ROI    
      ROIsum=0 
      for ch in ROI:
         ROIsum=ROIsum+int(ch)
      #    print ROIsum
      line.append(str(ROIsum))
   print(','.join(line), file=f)
 print("\b\b\b\b\b\b",i,end='')
print(" lines processed")  