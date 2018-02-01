### WORDSCORES (LBG-2003)
### author: Thiago Marzagao
### contact: marzagao ddott 1 at osu ddott edu

import os
import numpy as np
import pandas as pd

ipath = '/Users/username/inputdata/' # folder containing the CSV files
opath = '/Users/username/outputdata/' # folder where output will be saved

# hardcode your reference cases and their scores
Ar = pd.DataFrame({'referenceCase1': 1.1, # these are just examples
                   'referenceCase2': 3.7, 
                   'referenceCase3': 8.2},
                   index = ['score'])

# create function to load and merge data
def loadData(caseSet, path, cols):
    '''
    iterable, string, dict -> pandas.DataFrame
    '''
    output = pd.DataFrame(columns = ['word'])
    for case in caseSet:
    
        # check if case is casename or filename
        if '.csv' not in case:
            case = case + '.csv'

        # load new data file
        newData = pd.read_csv(path + case,
                              usecols = [col for col in cols.keys()],
                              dtype = cols,
                              names = ['word', case.replace('.csv', '')],
                              header = None)

        # merge with previous data
        output = pd.merge(output, newData, on = 'word', how = 'outer')
        output = output.fillna(0) # kill NaNs
                          
    return output

# load reference data
Fwr = loadData(Ar.keys(), ipath, {0: 'S30', 2: 'float'})

# compute p(r|w) = f_wr / sum(f_wr)_{for all r}
Pwr = Fwr.iloc[:, 1:].div(Fwr.sum(axis = 1), axis = 0)

# compute Sw and save to file
Sw = pd.DataFrame(Fwr.word)
Sw['score'] = Pwr.dot(Ar.T)
Sw.to_csv(opath + 'wordscores.csv', index = False)

# load virgin data
virginSet = [file for file in os.listdir(ipath) 
             if file.replace('.csv', '') not in Ar.keys()]
virginAbsFreq = loadData(virginSet, ipath, {0: 'S30', 1: 'int'})
Fwv = loadData(virginSet, ipath, {0: 'S30', 2: 'float'})

# 1:1 merge Fwv with Sw (to discard all disjoint words)
temp = pd.merge(Fwv, Sw, on = 'word', how = 'inner')

# split filtered Sw
cleanSw = pd.DataFrame(temp.score)

# clean up filtered Fwv
del temp['word']
del temp['score']
cleanFwv = temp

# compute Sv = sum(Fwv * Sw)_{for all w}
Sv = cleanFwv.T.dot(cleanSw)

# compute transformed Sv
Sv_t = (Sv - Sv.mean()) * (Ar.T.std() / Sv.std()) + Sv.mean()

# compute Vv
Vv = (cleanFwv * np.square((np.array(cleanSw) 
                            - np.array(Sv.T)))).sum(axis = 0)

# 1:1 merge absolute frequencies with Sw (to discard all disjoint words)
temp = pd.merge(virginAbsFreq, Sw, on = 'word', how = 'inner')

# compute N
del temp['word']
del temp['score']
N = temp.sum(axis = 0)

# compute standard errors and confidence intervals
std_error = np.sqrt(Vv / N)
lower = np.array(Sv).flatten() - np.array((1.96 * std_error))
upper = np.array(Sv).flatten() + np.array((1.96 * std_error))

# compute transformed confidence intervals
lower_t = (np.array(lower) - np.array(Sv.mean())) \
          * np.array((Ar.T.std() / Sv.std())) \
          + np.array(Sv.mean())
upper_t = (np.array(upper) - np.array(Sv.mean())) \
          * np.array((Ar.T.std() / Sv.std())) \
          + np.array(Sv.mean())

# print everything
print ''
print 'Original scores (w/ 95CI):'
print ''
Sv['lower'] = lower
Sv['upper'] = upper
print Sv
print ''
print 'Transformed scores (w/ 95CI):'
print ''
Sv_t['lower'] = lower_t
Sv_t['upper'] = upper_t
print Sv_t
print ''

# save transformed estimates to file
Sv_t.to_csv(opath + 'virginScores.csv', index_label = 'case')