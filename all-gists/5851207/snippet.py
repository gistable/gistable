### FIGHTIN' WORDS (MCQ-2008)   
### author: Thiago Marzagao     
### contact: marzagao ddott 1 at osu ddott edu

import os
import sys
import pandas as pd
import numpy as np
from numpy import matrix as m

rpath = '/Users/username/datafolder/' # folder of word-frequency matrices

# count number of word-frequency matrices
totalFiles = sum([1 for fileName in os.listdir(rpath) 
                  if fileName[-3:] == 'csv']
                  if fileName != 'corpus.csv')

# quit if no word-frequency matrices found
if totalFiles == 0:
    sys.exit('No word-frequency matrices in {}'.format(rpath))

# load word-frequency matrices
docNames = []
y = pd.DataFrame(columns = ['word'])
for fileName in os.listdir(rpath):
    if fileName[-3:] == 'csv' and fileName != 'corpus.csv':
    
        # clean up document name
        document = fileName.replace('.csv', '')
        document = document.replace('-', '')
        docNames.append(document)

        # load frequencies
        y_i = pd.read_csv(rpath + fileName, 
                          usecols = [0, 1], 
                          dtype = {0: 'S30', 1: 'int'}, 
                          names = ['word', document], 
                          header = None)
        
        # merge with previous ones
        y = pd.merge(y, y_i, on = 'word', how = 'outer')

        # kill NaNs
        y = y.fillna(0)

# choose prior
print ''
priorChoice = int(input('Uninformative (1) or informative (2) prior? '))
if priorChoice == 1:
    alpha_i = m.transpose(m([0.01] * len(y)))
elif priorChoice == 2:
    priors = pd.read_csv(rpath + 'corpus.csv', # load global frequencies
                         usecols = [0, 1], 
                         names = ['word', 'gfreq'], 
                         header = None)
    y = pd.merge(y, priors, on = 'word', how = 'left') # merge w/ y
    y = y.fillna(y['gfreq'].min()) # replace missing by argmin(alphas)
    alpha_i = m.transpose(m(y.gfreq)) # extract alphas
    del y['gfreq'] # clean up y
else:
    sys.exit('Invalid choice')

# estimate p_i
yword = m.transpose(m(np.hstack((['word'], np.array(y.word))))) # word list
y_i = m(y.iloc[:, 1:])
n_i = y_i.sum(axis = 0)
alpha0_i = alpha_i.sum(axis = 0)
p_i = (y_i + alpha_i) / (n_i + alpha0_i)

# estimate delta_i
y = m(y.iloc[:, 1:]).sum(axis = 1)
n = y.sum(axis = 0)
alpha = alpha_i.sum(axis = 1)
alpha0 = alpha.sum(axis = 0)
lomega_i = np.log((y_i + alpha_i) / ((n_i + alpha0_i) - (y_i + alpha_i)))
lomega = np.log((y + alpha) / ((n + alpha0) - (y + alpha)))
delta_i = lomega_i - lomega

# estimate delta_(i - j)_{for all (i, j)}
delta_ij = m(np.zeros((len(lomega_i), 1))) # initialize delta_ij
for col in range(0, lomega_i.shape[1] - 1): # delta_(i - j)_{for all (i, j)}
    delta_ij = np.hstack((delta_ij, lomega_i[:, col] 
                          - lomega_i[:, (col + 1):]))
delta_ij = np.delete(delta_ij, 0, 1)
    
# estimate sigma2_i
sigma2_i = (1 / (y_i + alpha_i)) + (1 / (y + alpha))

# estimate sigma2_(i - j)_{for all (i, j)}
yi_alphai = 1 / (y_i + alpha_i)
sigma2_ij = m(np.zeros((len(sigma2_i), 1))) # initialize sigma2_ij
for col in range(0, yi_alphai.shape[1] - 1): # sigma2_(i - j)_{for all (i, j)}
    sigma2_ij = np.hstack((sigma2_ij, yi_alphai[:, col] 
                           + yi_alphai[:, (col + 1):]))
sigma2_ij = np.delete(sigma2_ij, 0, 1)

# estimate z_i
z_i = delta_i / np.sqrt(sigma2_i)

# estimate z_(i - j)_{for all (i, j)}
z_ij = delta_ij / np.sqrt(sigma2_ij)

# generate colnames for z_(i - j)
colNames = []
for i in range(0, len(docNames)):
    for j in range(1, len(docNames)):
        if i < j:
            colName = docNames[i] + '_' + docNames[j]
            colNames.append(colName)

# format z_(i - j) matrix and save
toFile = np.vstack((m(colNames), z_ij)) # append document names
toFile = pd.DataFrame(np.hstack((yword, toFile))) # append word list
toFile.to_csv(rpath + 'zScores_ij.csv',  # save to file
              index = False,
              header = False)

# wrap up
print ''
print 'Done! All files successfully processed'
print 'Output saved to', rpath
print ''