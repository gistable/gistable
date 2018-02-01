#/usr/bin/env python
import pybel

#this loads a known problematic molecule from the ZINC (ZINC39141032)
mol = pybel.readstring('smi','C1CCC[NH+](CC1)C[C@@H]2CCC[NH2+]2')

#The bug is only triggered if the 'MACCS' fingerprint is calculated before HBA2
#If the HBA2 are calculated before the fingerprint, it works.

print mol.calcfp('MACCS') 
print mol.calcdesc(['HBA2'])

print 'it worked!!'

raw_input() #This is here in order to be able to see the window on Windows if it works