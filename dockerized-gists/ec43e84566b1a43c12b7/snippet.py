#!/bin/python
#xkcd SFS plots
# usage: ms 20 10000 -t 50 -r 10 1000  > neutral_ms.txt; python XKCD_sfs_plots.py neutral_ms.txt

from matplotlib import pyplot as plt
import numpy as np
from itertools import groupby
from sys import argv

ms_file = open(argv[1])

ms_list = list(ms_file)

ms_list2 = [list(group) for k, group in groupby(ms_list, lambda x: x == "//\n") if not k]

final_sfs = []
for rep, sim in enumerate(ms_list2):
    positions = []
    snpmatrix = []
    if any("ms" in s for s in sim):
        continue
    positions = [s for s in sim if "positions" in s] # grab the positions line from the output
    start_mat = sim.index(positions[0])

    snpmatrix = sim[start_mat+1:]
    snpmatrix.pop(-1)
    snpmatrix = [list(s.strip()) for s in snpmatrix]
    snpmatrix = zip(*snpmatrix)

    sfs = np.zeros(len(snpmatrix[0]))

    for pos in snpmatrix:
        num_mutations =  pos.count('1')
        if num_mutations == 0:
            continue
        sfs[num_mutations-1] = sfs[num_mutations-1]+1
    final_sfs.append(sfs)

sfs_lengths = [len(x) for x in final_sfs]

data = np.zeros(max(sfs_lengths))

for sfs in final_sfs:
    if len(sfs) < len(data):
        size_diff = len(data) - len(sfs)
        sfs = np.lib.pad(sfs, (0,size_diff), "constant", constant_values=0)
    data = np.add(data, sfs)

if data[-1] == 0:
    data = np.delete(data, -1)
data = np.insert(data, 0, 0)
plt.xkcd()

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
plt.xticks(xrange(1, len(data)))
plt.yticks([])
ax.set_xlim([1, len(data)])
ax.set_ylim([0, np.amax(data)])

plt.plot(data, 'r-.')

plt.title("SITE FREQUENCY SPECTRUM")
plt.xlabel('NUMBER OF MUTATIONS')
plt.ylabel('FREQUENCY')

plt.show()
