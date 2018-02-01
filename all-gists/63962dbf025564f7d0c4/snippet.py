#!/usr/bin/python

import re
import sys
import shlex


inputfile = sys.argv[1]
outputfile = sys.argv[2]


table_name = None
unique_keys = []
keys = []
foreign_keys = []
columns = []
key_count = 0
unique_key_count = 0

with open(inputfile) as iff:
    for line in iff:
        line = line.rstrip()
        if line.startswith('/*') or line.startswith('--'):
            continue
        sl = shlex.shlex(line)
        sl.whitespace_split = True
        col = list(sl)
        if len(col) == 0:
            continue
        if table_name is None:
            if col[0] == "LOCK":
                continue
            elif col[0] == "UNLOCK":
                continue
            if len(col) >= 2:
                if  col[0:2] == ["CREATE", "TABLE"]:
                    table_name = col[2]
                    unique_keys = []
                    keys = []
                    columns = []
                elif col[0:2] == ["INSERT", "INTO"]:
                    col[2] = col[2].strip("`")
            #col = [x.strip('`') for x in col]
            print(' '.join(col))
            continue
        else:
            last_col = col[-1]
            col[-1] = last_col.rstrip(',')
            if len(col) >= 1 and col[0] == ')':
                #print("columns: %s" % columns)
                if len(columns) > 0:
                    last_column = columns.pop()
                    for i in columns:
                        print(i + ",")
                    print(last_column)
                print(');')
                for key in keys:
                    print("CREATE INDEX %s ON %s %s;" % \
                          (key[0], table_name, key[1]))
                for key in unique_keys:
                    print("CREATE UNIQUE INDEX %s ON %s %s;" % \
                          (key[0], table_name, key[1]))
                table_name = None
            elif len(col) >= 1 and col[0] == 'KEY':
                keys.append(["key_%d" % key_count, col[2]])
                key_count += 1
                continue
            elif len(col) >= 2 and col[0:2] == ['UNIQUE', 'KEY']:
                unique_keys.append(["unique_key_%d" % unique_key_count,
                                   col[3]])
                unique_key_count += 1
                continue
            elif len(col) >= 1 and col[0] == 'CONSTRAINT':
                col = col[2:] + ['DEFERRABLE', 'INITIALLY', 'DEFERRED']
            elif len(col) >= 2 and col[1].startswith('char('):
                col[1] = 'TEXT'
            elif len(col) >= 2 and col[1].startswith('varchar('):
                col[1] = 'TEXT'
            elif len(col) >= 2 and col[1].startswith('int('):
                col[1] = 'INTEGER'
            elif len(col) >= 2 and col[1].startswith('float('):
                col[1] = 'REAL'
            elif len(col) >= 2 and col[1].startswith('enum('):
                col[1] = 'TEXT'
            new_col = []
            for i in col:
                if i == "unsigned":
                    continue
                elif i == "utf8_unicode_ci":
                    i = "nocase"
                elif i == "AUTO_INCREMENT":
                    i = "UNIQUE"
                new_col.append(i)
            col = new_col
            columns.append(' '.join(col))
