""" 
Parse output of nvidia-smi into a python dictionary.
This is very basic!
"""

import subprocess
import pprint

sp = subprocess.Popen(['nvidia-smi', '-q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

out_str = sp.communicate()
out_list = out_str[0].split('\n')

out_dict = {}

for item in out_list:
    try:
        key, val = item.split(':')
        key, val = key.strip(), val.strip()
        out_dict[key] = val
    except:
        pass

pprint.pprint(out_dict)