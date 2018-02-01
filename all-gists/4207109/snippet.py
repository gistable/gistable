#!/usr/bin/env python
"""Convert a master latex file,
into a single document by including
automatically all the LaTeX documents 
which are arguments of 
\include or \input
ignoring any \includeonly
"""
import sys
if len(sys.argv)==3:
    masterfile=sys.argv[1]
    flattenfile=sys.argv[2]
else:
    sys.exit('USAGE: %s masterfile.tex flattenfile.tex' %sys.argv[0])
    
filetex=open(masterfile,'r')
texlist=filetex.readlines()
finaltex=open(flattenfile,'w')
for i in texlist:
    if i.find(r'\input{')==0 or i.find(r'\include{')==0: 
        includetex=open(i.split('{')[-1].split('}')[0]+'.tex','r')
        finaltex.write(includetex.read())
        finaltex.write('\n')
    elif i.find(r'\includeonly{')==0:
        finaltex.write(i.replace(r'\includeonly{',r'%\includeonly{'))
    else:
        finaltex.write(i) 
        
        
filetex.close()
finaltex.close()