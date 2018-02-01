#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import subprocess
import argparse

def main(work_dir, target_ext, from_encoding, to_encoding):
    for current_dir, dirnames, fnames in os.walk(work_dir):
        for fname in fnames:
            _, ext = os.path.splitext(fname)
            if ext.lower() == target_ext:
                out_fname = "_".join([to_encoding, fname])
                out_path = os.path.join(current_dir, out_fname)
                input_path = os.path.join(current_dir, fname)
                print("processing {}".format(input_path))
                cmd = " ".join(["iconv", "-f", from_encoding, 
                                "-t", to_encoding, "-c",
                                input_path,
                                ">", out_path])
                try:
                    subprocess.call(cmd, shell = True)
                except Exception as e:
                    print("Fail to process {}".format(input_path),
                          file = sys.stderr)
                    print(e)

def _encoding_type(argstr):
    if not argstr is None:
        return argstr
    
    if sys.platform in ["win32", "cygwin"]:
        return "big5"
    else:
        return "utf8"
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--work-dir", metavar = "DIR_NAME",
                        dest = "work_dir",
                        help = "working directory (default: .)", default = ".")
    parser.add_argument("-f", "--from-encoding", metavar = "ENCODING_NAME",
                        dest = "from_encoding", required = True,
                        help = "from encoding (required)")
    parser.add_argument("-t", "--to-encoding", metavar = "ENCODING_NAME",
                        dest = "to_encoding",
                        help = "to encoding (default: None, will infered by the platform)",
                        type = _encoding_type, default = _encoding_type(None))
    parser.add_argument("-e", "--target-ext", metavar = "FILE_EXT",
                        dest = "target_ext",
                        help = "target file extension (default: .csv)",
                        type = str, default = ".csv")
    args = parser.parse_args()
    main(args.work_dir,
         args.target_ext,
         args.from_encoding,
         args.to_encoding)
                    