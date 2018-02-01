import re
import os
import sys

filename = sys.argv[1]
headerName = os.path.basename(filename).split('.')[0] + '.h'

with open(filename) as file:
    print('#include "' + headerName + '"')
    print('#include "unimplemented.h"')
    print()
    
    for line in file:
        match = re.match(r"class (\w+) {", line)
        if match is not None:
            className = match.group(1)
        
        match = re.match(r"namespace (\w+) {", line)
        if match is not None:
            namespaceName = match.group(1)
            print('using namespace ' + namespaceName + ';')
            print()
            
        match = re.match(r"\s*([^\(^\s]+\([^\)]*\))", line)
        if match is not None:
            print('#warning Please add implementation for ' + match.group(1))
            print(className + '::' + match.group(1) + '{}')
            print()
        
        match = re.match(r"\s*([^\s]+) ([^\w]*)([^\(]+\([^\)]*\))", line)
        if match is not None:
            print('UNIMPLEMENTED(' + match.group(1) + ' ' + match.group(2) + className + '::' + match.group(3) + ')')
            print()

