#!/usr/bin/env python
# Still writing this, but wanted to share progress before creating a repo for this project

import os
import re
import traceback

path = "Person of Interest - 05x13 - Return 0.LOL.English.C.orig.Addic7ed.com.srt"

####################################################################################################
def del_addic7ed(data):
    start_line_index = None
    for i, line in enumerate(data):
        ri = re.search(r'^(\d+)\r\n$', line)
        if ri:
            start_line_index = i

        if re.search(r'(www\.addic7ed\.com)', line) and start_line_index:
            print data[start_line_index:i+1]
            del data[start_line_index:i+1]
            return data

    return data

####################################################################################################
def clean_list(data):
    match = True
    count = 0

    while match or (count <= 5):
        count += 1
        if re.search(r'(www\.addic7ed\.com)', ''.join(data)):
            data = del_addic7ed(data)
        else:
            match = False

    return data

####################################################################################################
def update_index(data):
    count = 0
    for i, line in enumerate(data):
        if re.search(r'^(\d+)\r\n$', line):
            count += 1
            re.sub(r'(\d+)', str(count), data[i])

    return data

####################################################################################################
def load_srt(path):
    data = None
    try:
        with open(path, 'r') as f:
            data = f.readlines()
    except Exception as e:
        print('Load Error: %s' %str(e))
        traceback.print_exc()

    return data

####################################################################################################
def save_srt(path, data):
    try:
        with open(path, 'w') as f:
            f.write(''.join(data).strip())
    except Exception as e:
        print('Save Error: %s' %str(e))
        traceback.print_exc()

        return False
    return True

####################################################################################################
def remove_addic7ed(file_path):
    data = load_srt(file_path)
    if data:
        data = clean_list(data)
        data = update_index(data)
        if not save_srt(file_path, data):
            return False
        return "Awww Yisss, %s all clean!" %file_path

    return False

print remove_addic7ed(path)