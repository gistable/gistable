import re

regexp = re.compile('=([0-9]*)mol=')
txt = 'wDARL=1234mol=1000Lamo.1000.dat'
search = regexp.search(txt)
results = search.groups()
if len(results)>0:
    print(results[0])