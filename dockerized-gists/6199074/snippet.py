#!/usr/bin/env python
#-*- coding: utf8 -*-

from __future__ import print_function
from optparse import OptionParser
import zipfile
from sys import argv, exit
from subprocess import Popen, PIPE, check_output
import os.path


find_bin_path = lambda bin_name: check_output(["which", bin_name])
fn_base_extension = lambda fn: os.path.splitext(fn)


def opencc_convert_s2t(text, opencc_bin_path):
    try:
        proc = Popen([opencc_bin_path], stdin=PIPE, stdout=PIPE)
        proc.stdin.write(text.encode('utf8'))

        code = proc.poll()
        if code:
            raise RuntimeError('Failed to call opencc with exit code {0}'.format(code))

        result = proc.communicate()[0]

        return result.decode('utf8')

    except OSError:
        return ""


def convert_epub_sc2tc(input_fn, output_fn, opencc_bin_path):
    # read epub file and convert
    file_exts = ['.html', '.htm', '.ncx', '.opf', '.xhtml']

    input_fh = zipfile.ZipFile(input_fn, "r")
    fn_list_sc, fn_list_bin = reduce(lambda (fn_sc, fn_bin), fn:
                                     (fn_sc + [fn], fn_bin)
                                     if any(fn.endswith(x) for x in file_exts)
                                     else (fn_sc, fn_bin + [fn]),
                                     input_fh.namelist(), ([], []))

    read_zip = lambda fn: input_fh.read(fn).replace('zh-CN', 'zh-TW').decode('utf8')
    content_list_tc = [opencc_convert_s2t(read_zip(fn), opencc_bin_path)
                       for fn in fn_list_sc]
    content_list_bin = [input_fh.read(fn) for fn in fn_list_bin]

    input_fh.close()

    # write epub file
    out_fh = zipfile.ZipFile(output_fn, "w")
    map(lambda (fn, content): out_fh.writestr(fn, content.encode('utf8')),
        zip(fn_list_sc, content_list_tc))
    map(lambda (fn, content): out_fh.writestr(fn, content),
        zip(fn_list_bin, content_list_bin))

    out_fh.close()


def get_option_args(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output",  dest="output", action="store",
                      default="", type="string", help="output input file name")

    option, args = parser.parse_args(argv)

    fn_list = [fn for fn in args[1:] if fn_base_extension(fn)[1] == '.epub']
    if not fn_list:
        parser.print_help()
        exit(1)

    if option.output:
        return zip(fn_list, [option.output])
    else:
        return zip(fn_list,
                   [fn_base_extension(fn)[0] + "_tc.epub" for fn in fn_list])


def main():
    opencc_bin_path = find_bin_path('opencc').strip()

    if not opencc_bin_path:
        print("Please install opencc and check opecc in your $PATH")
        exit(1)

    in_out_fn_list = get_option_args(argv)

    for in_fn, out_fn in in_out_fn_list:
        convert_epub_sc2tc(in_fn, out_fn, opencc_bin_path)
        print("Convert {0} to {1} sucessfully.".format(in_fn, out_fn))

if __name__ == "__main__":
    main()
