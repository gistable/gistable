#!/usr/bin/env python
"""
FUNCTION: Converts a CSV (tab delimited) file to an Excel xlsx file.

Copyright (c) 2016, Konrad Foerstner <konrad@foerstner.org>

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that the
above copyright notice and this permission notice appear in all
copies.

THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
         
"""

import argparse
import csv
import sys
from openpyxl import Workbook


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()

    if not args.input_file.endswith(".csv"):
        sys.stderr.write("Error: File does not have the ending \".csv\".\n")
        sys.exit(2)
 
    wb = Workbook()
    worksheet = wb.active
    for row in csv.reader(open(args.input_file), delimiter="\t"):
        worksheet.append([_convert_to_number(cell) for cell in row])
    wb.save(args.input_file.replace(".csv", ".xlsx"))


def _convert_to_number(cell):
    if cell.isnumeric():
        return int(cell)
    try:
        return float(cell)
    except ValueError:
        return cell

main()