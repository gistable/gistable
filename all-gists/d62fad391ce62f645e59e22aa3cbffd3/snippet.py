#! /usr/local/bin/python3

import json
import sys

with open(sys.argv[1], mode='r+', encoding='UTF-8') as plane :
    json_list = json.load(plane)
    plane.write(json.dumps(json_list))