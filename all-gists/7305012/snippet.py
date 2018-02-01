import json
import os
from collections import defaultdict
from random import sample

population = defaultdict(list)
sample_size = 2
final_sample = defaultdict(list)

# i = getIncident('blahblahblah.json')
def getIncident(inString):
  return json.loads(open(inString).read())

for filename in os.listdir('.'):
    if filename.endswith('.json'):
        i = getIncident(filename)
        if 'analysis_status' not in i['plus'].keys():
            population['no status'].append(filename)
            continue
        if i['plus']['analysis_status'] == "First pass":
            try:
                population[i['plus']['analyst']].append(filename)
            except:
                population['no analyst'].append(filename)

for key in population.keys():
    if len(population[key]) >= sample_size:
        final_sample[key] = sample(population[key],sample_size)
    else:
        final_sample[key] = sample(population[key],len(population[key]))

for key in final_sample:
    print "Sample for",key
    for each in final_sample[key]:
        print "\t",each