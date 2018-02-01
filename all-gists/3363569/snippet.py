#!/usr/bin/python                                                                                                                                                                  

import sys

if  __name__ == '__main__':
    filename = sys.argv[1];
    input = open(filename)
    output = open(filename + '.out', 'w')

    for line in input:
        if line.startswith('#. '):
            output.write(line.replace('#. ', ''))

        elif line.startswith('#: '):
            output.write(line.replace('#: ', '"').replace('\n', '" = '))

        elif line.startswith('msgstr '):
            output.write(line.replace('msgstr ', '').replace('\n', ';\n\n'))

    input.close()
    output.close()