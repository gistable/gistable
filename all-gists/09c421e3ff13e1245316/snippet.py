import argparse
import json
import re
import os
from time import time

parser = argparse.ArgumentParser(description='Convert to Quiver Format')
parser.add_argument("src", help="The Source File You want to Convert")
args = parser.parse_args()
cells = []
lines = []

with open(args.src) as f:
    for row in f.readlines():
        lines.append(row)

markdown = re.findall(r"`?`?`?([^`]*)```py", ''.join(lines))
code = re.findall(r"```py([^`]*)```", ''.join(lines))
length = len(markdown)
markdown_start = True
if len(code) > length:
    length = len(code)
    markdown_start = False

for x in range(length):
    try:
        if markdown_start:
            cells.append({
            "type": "markdown",
            "data": markdown[x].strip("\n")
            })
            cells.append({
            "type": "code",
            "language": "python",
            "data": code[x].strip("\n")
            })
        else:
            cells.append({
            "type": "code",
            "language": "python",
            "data": code[x].strip("\n")
            })
            cells.append({
            "type": "markdown",
            "data": markdown[x].strip("\n")
            })
    except:
        pass

content = {"title": args.src.split('.')[0], "cells": cells}
meta = {
  "created_at" : int(time()),
  "tags" : [],
  "title" : args.src.split('.')[0],
  "updated_at" : int(time())
}
newpath = args.src.split('.')[0] + '.qvnote'
if not os.path.exists(newpath): os.makedirs(newpath)
with open(args.src.split('.')[0] + '.qvnote' + "/content.json", 'wb') as f:
    json.dump(content, f)

with open(args.src.split('.')[0] + '.qvnote' + "/meta.json", 'wb') as f:
    json.dump(content, f)



# print content
# with open("content.json", 'wb') as f:
#     json.dump(content, f)
