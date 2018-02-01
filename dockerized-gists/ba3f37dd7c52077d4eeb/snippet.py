# -*- coding: utf-8 -*-
"""
Sample report generation script from pbpython.com

This program takes an input Excel file, reads it and turns it into a
pivot table.

The output is saved in multiple tabs in a new Excel file.
"""

import argparse
import pandas as pd
import numpy as np


def create_pivot(infile, index_list=["Manager", "Rep", "Product"],
                 value_list=["Price", "Quantity"]):
    """
    Read in the Excel file, create a pivot table and return it as a DataFrame
    """
    df = pd.read_excel(infile)
    table = pd.pivot_table(df, index=index_list,
                           values=value_list,
                           aggfunc=[np.sum, np.mean], fill_value=0)
    return table


def save_report(report, outfile):
    """
    Take a report and save it to a single Excel file
    """
    writer = pd.ExcelWriter(outfile)
    for manager in report.index.get_level_values(0).unique():
        temp_df = report.xs(manager, level=0)
        temp_df.to_excel(writer, manager)
    writer.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to generate sales report')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help="report source file in Excel")
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help="output file in Excel")
    args = parser.parse_args()
    # We need to pass the full file name instead of the file object
    sales_report = create_pivot(args.infile.name)
    save_report(sales_report, args.outfile.name)

