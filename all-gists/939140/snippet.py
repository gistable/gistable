#!/usr/bin/env python

import re, collections
from subprocess import *

def sanitize_keybinding(binding):
    d = {'space': ' ',
         'apostrophe': "'",
         'BackSpace': ' (<-)',
         'Return': '↵ \n',
         'period': '.',
         'Shift_L1': ' (shift1) ',
         'Shift_L2': ' (shift2) '}
    if binding in d:
        return d[binding]
    else:
        return binding
    

def get_keymap():
    keymap = {}
    table = Popen("xmodmap -pke", shell=True, bufsize=1, stdout=PIPE).stdout
    for line in table:
        m = re.match('keycode +(\d+) = (.+)', line.decode())
        if m and m.groups()[1]:
            keymap[m.groups()[0]] = sanitize_keybinding(m.groups()[1].split()[0])
    return keymap
        

if __name__ == '__main__':
    logger = Popen("xinput test 9", shell=True, bufsize=1, stdout=PIPE).stdout
    counts = collections.defaultdict(lambda : 0)
    output = []

    try:
        for line in logger:
            m = re.match('key press +(\d+)', line.decode())
            if m:
                keycode = m.groups()[0]
                counts[keycode] += 1
                output.append(keycode)
    except KeyboardInterrupt:
        keymap = get_keymap()
        print(output)
        print("---------------------")
        print(''.join(map(lambda x: keymap[x] if x in keymap else '?', output)))
        
