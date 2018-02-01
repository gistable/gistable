#!/usr/bin/env python

import sys

program = sys.argv[1]

jump = {}

_brackets = []
for i in range(len(program)):
    if program[i] == '[':
        _brackets.append(i)
    elif program[i] == ']':
        j = _brackets.pop()
        jump[i] = j
        jump[j] = i

memory = 30000 * [0]

p = 0

def inc():
    global p
    p = p + 1

def dec():
    global p
    p = p - 1

def inc_byte():
    memory[p] = memory[p] + 1

def dec_byte():
    memory[p] = memory[p] - 1

def out_byte():
    sys.stdout.write(chr(memory[p]))

def in_byte():
    char = sys.stdin.read(1)
    if char != "":
        memory[p] = ord(char)
    else:
        return 1
 
command = { '>': inc     , '<': dec      , 
            '+': inc_byte, '-': dec_byte , 
            '.': out_byte, ',': in_byte  }

index = 0

while True:
    if index == len(program):
        break
    else:
        char = program[index]
        #print "*", index, char
        if char == '[':
            if memory[p] == 0:
                index = jump[index]
            else:
                index = index + 1
        elif char == ']':
            if memory[p] != 0:
                index = jump[index]
            else:
                index = index + 1
        else:
            cmd = command[char]
            error = cmd()
            if error: # EOF
                break
            index = index + 1
