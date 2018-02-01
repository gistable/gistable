#! /usr/bin/env python
import re
# Sample input to test
crude = '''
BGP table version is 0, local router ID is 10.0.0.2
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, R Removed
Origin codes: i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*  172.31.1.0/24    40.0.0.4                               0 7678 7675 i
*>                  10.0.0.1                 0             0 7675 i
*> 172.31.2.0/24    0.0.0.0                  0         32768 i
*> 172.31.3.0/24    10.0.0.1                               0 7675 7677 i
*                   40.0.0.4                               0 7678 7677 i
*  172.31.4.0/24    10.0.0.1                               0 7675 7678 i
*>                  40.0.0.4                 0             0 7678 i
*> 000.00.0.0/00    00.0.0.0                 0      0      0 7678 0000 i

Total numberof prefixes 4
'''

keys = ["Type", "Network", "Next_Hop", "Metric", "LocPrf", "Weight", "Path"] # These keys are used only to mount the final dictionary
# crude = ''.join(info)
lines = crude.split('\n\n')[1].split('\n')
header = lines.pop(0) # Removing the useless header
header = header.replace('Next Hop', 'Next_Hop') # Go Horse!

header = re.split(r' [a-zA-Z]', header) # Spliting the header selecting the first string after a space
header[0] = header[0][0:-1] # First column only lose one char so remove another one here
output = []
regex = []

# Creating the regexp to break the BGP table from header column size
for column in header:
  if column == header[-1]:
    regex.append("(.+)")
    break
  regex.append("(.{%s})" %str(len(column)+2))

regex = ''.join(regex) # As regex must be an string, convert the array.

# From the regex break the line into pieces and then create the final dict
for line in lines:
  values = re.findall(regex, line)
  values = [x.strip() for x in values[0]]

  output.append(dict(zip(keys, values)))

for index in range(len(output)):
  if output[index].get('Network') == '':
    output[index]['Network'] = output[index-1]['Network']

print output
