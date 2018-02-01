#!/usr/bin/env python

import re
import shutil

#
# Reads a source file and remove code associated with VTKv5.
#
# Only cpp file are considered.
#
#
# Cpp files:
#
# Given the a valid cpp file in input, it will
# look for structure matching the following:
#
# 0:                              // STATE_NORMAL
# 1: #include <vtkVersion.h>      // STATE_NORMAL
# 2: [...]                        // STATE_NORMAL
# 3: #if (VTK_MAJOR_VERSION <= 5) // STATE_IF
# 4: [...]                        // STATE_IF
# 5: #else                        // STATE_ELSE
# 6: [...]                        // STATE_ELSE
# 7: #endif                       // STATE_ELSE
# 8:                              // STATE_NORMAL
#
#
# Considering the example above, the selected ranges will be:
#
# (1, 1)  <- Include of vtkVersion.h
# (3, 5)  <- #if / #else range
# (7, 7)  <- Line with #endif
#
#
# Assumption(s):
#
#  * Input source file is valid c++ code
#
#
# Limitation(s):
#
#  * Do not support multiple level of #if. The state machine would have to
#  improved.
#
#
# Internally it will associate each line with one of these three states:
#
STATE_NORMAL = 0
STATE_IF = 1
STATE_ELSE = 2

#
# The following cases are considered (with and without parentheses):
#
#  case 1:
#    #if (VTK_MAJOR_VERSION <= 5)
#    #if (VTK_MAJOR_VERSION < 6)
#
#  case 2:
#    #if (VTK_MAJOR_VERSION > 5)
#    #if (VTK_MAJOR_VERSION >= 6)
#

def update_source_file(source_file):

    to_remove = []
    state = STATE_NORMAL

    canditates_case1 = [
      re.compile(r'#if\s*[\(]?VTK_MAJOR_VERSION\s*\<\=\s*5[\)]?'),
      re.compile(r'#if\s*[\(]?VTK_MAJOR_VERSION\s*\<\s*6[\)]?')
      ]
 
    canditates_case2 = [
      re.compile(r'#if\s*[\(]?VTK_MAJOR_VERSION\s*\>\s*5[\)]?'),
      re.compile(r'#if\s*[\(]?VTK_MAJOR_VERSION\s*\>\=\s*6[\)]?')
      ]

    regex_else = re.compile(r'#\s*else')

    regex_endif = re.compile(r'#\s*endif')

    with open(source_file, 'r') as myfile:
        previous_line = -1
        remove_if_else = None # True: canditates_case1, False: canditates_case2
        lines = myfile.readlines()
        for (line_number, line) in enumerate(lines):
            line = line.strip()

            if state == STATE_NORMAL and line == '#include <vtkVersion.h>':
                to_remove.append((line_number, line_number))
            if state == STATE_NORMAL:
                remove_if_else = None
                for regex in canditates_case1:
                    if regex.match(line) is not None:
                        remove_if_else = True
                        break
                if remove_if_else is None:
                    for regex in canditates_case2:
                        if regex.match(line) is not None:
                            remove_if_else = False
                            break

                if remove_if_else is not None:
                    state = STATE_IF

                if remove_if_else is False:
                    to_remove.append((line_number, line_number + 1))

                previous_line = line_number
                    

            if state == STATE_IF and (regex_else.match(line) or regex_endif.match(line)):
                # Keep track of the range to remove
                if remove_if_else:
                    to_remove.append((previous_line, line_number + 1))
                previous_line = line_number
                # Update state ivar
                if regex_else.match(line):
                    state = STATE_ELSE
                elif regex_endif.match(line):
                    state = STATE_NORMAL
                    if remove_if_else is False:
                        to_remove.append((line_number, line_number + 1))

            if state == STATE_ELSE and regex_endif.match(line):
                # Keep track of the line to remove
                if remove_if_else:
                    to_remove.append((line_number, line_number + 1))
                else:
                    to_remove.append((previous_line, line_number + 1))
                # Update state ivars
                previous_line = -1
                state = STATE_NORMAL

    while len(to_remove) > 0:
        _range = to_remove.pop()
        del lines[_range[0]:_range[1]]
        
    with open(source_file + '.tmp', "w") as myfile:
        myfile.writelines(lines)

    shutil.move(source_file + ".tmp", source_file)

    print("%s [Done]" % source_file)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Remove VTKv5 support from source files.')
    parser.add_argument('files', type=str, nargs='+',
                       help='Valid Cpp Source files')

    args = parser.parse_args()

    for source_file in args.files:
        update_source_file(source_file)
    
