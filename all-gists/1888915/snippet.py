#!/usr/bin/env python

import os
import sys

SOURCE_FILE = "/home/cmthunes/enwiki-20120211-pages-meta-current.xml"
OUTPUT_FILE = "/mnt/reports/cmthunes/enwiki-20120211.json"

def extract_with_delims(s, start_delim, end_delim):
    start_index = s.find(start_delim)
    if start_index == -1:
        return None

    end_index = s.find(end_delim)
    if end_index == -1:
        return None

    if end_index <= start_index:
        return None

    start_index += len(start_delim)

    return s[start_index:end_index]

def extract_data(part):
    title = extract_with_delims(part, "<title>", "</title>")
    timestamp = extract_with_delims(part, "<timestamp>", "</timestamp>")
    text = extract_with_delims(part, "<text xml:space=\"preserve\">", "</text>")

    return (title, timestamp, text)

def json_encode_string(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("/", "\\/")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\t", "\\t")
    return '"' + s + '"'

def split_records():
    enwikisource = open(SOURCE_FILE)
    text_buffer = ""
    
    start_index = 0
    end_index = 0

    while True:
        chunk = enwikisource.read(16 * 1024 * 1024)

        if chunk:
            text_buffer += chunk

        start_index = 0
        end_index = 0

        while True:
            start_index = text_buffer.find("<page>", start_index)

            # No pages in the buffer, continue loading data
            if start_index == -1:
                break

            end_index = text_buffer.find("</page>", end_index)

            # No complete page in buffer
            if end_index == -1:
                break

            yield text_buffer[start_index:end_index + len("</page>")]

            start_index = end_index + len("</page>")
            end_index = start_index

        # No more data
        if chunk == "":
            break

        if start_index == -1:
            text_buffer = ""
        else:
            text_buffer = text_buffer[start_index:]

if os.path.exists(OUTPUT_FILE):
    print "Output file already exists. Please remove first so I don't destroy your stuff please"
    sys.exit(1)
            
json_file = open(OUTPUT_FILE, "w")
template = '{"title": %s, "timestamp": %s, "text": %s},\n'
i = 0

json_file.write("[\n")

try:
    for page in split_records():
        i += 1
        sys.stdout.write("\r%d" % (i,))
        sys.stdout.flush()

        title, timestamp, text = extract_data(page)

        if None in (title, timestamp, text):
            continue

        json_file.write(template % tuple(map(json_encode_string, 
                                             (title, timestamp, text))))
finally:
    json_file.write("]\n")
    json_file.close()
    print
