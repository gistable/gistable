#! /usr/bin/env python3
# Convert all markdown files in the current folder to PDF using pandoc
import os
import subprocess
import time

MARKDOWN_EXTS = ('.markdown', '.md')
# Using abspath means I don't have to manually specify the folder name
ROOT_FOLDER = os.path.split(os.path.abspath(__file__))[0]

os.chdir(ROOT_FOLDER)
dir_ls = os.listdir(ROOT_FOLDER)

# Read in the last time the script was run,
# if it's been run at all
if not os.path.exists(".notes_last_created"):
    LAST_RUN = 0
else:
    with open(".notes_last_created") as time_file:
        LAST_RUN = float(time_file.read().strip())

if not os.path.exists("PdfNotes"):
    os.mkdir("PdfNotes")

for current_file in dir_ls:
    name, ext = os.path.splitext(current_file)
    if ext in MARKDOWN_EXTS:
        # Check if the markdown file has been updated since last time the
        # script was run
        if os.stat(current_file).st_mtime > LAST_RUN:
            print("Updating", current_file)
            out_file = os.path.join(ROOT_FOLDER, "PdfNotes", name + ".pdf")
            subprocess.call([
                "pandoc",
                current_file,
                "-o",
                out_file,
                "--highlight-style=Zenburn",
                "--number-sections",
                # Table of contents
                "--toc"
            ])

with open(".notes_last_created", "w") as time_out:
    time_out.write(str(time.time()))