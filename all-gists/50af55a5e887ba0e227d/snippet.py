#!/usr/bin/python3

# pip3 install markdown

template = """<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="utf-8">
</head>
<body>
    %s
</body>
</html>
"""

import os
import markdown

files = os.listdir(".")
files = [file for file in files if file.endswith(".md")]
files.sort(reverse=True)

contents = [open(file, "r").read() for file in files]
contents = "\n\n".join(contents)
contents = markdown.markdown(contents)
contents = template % contents

open("all.html", "w").write(contents)