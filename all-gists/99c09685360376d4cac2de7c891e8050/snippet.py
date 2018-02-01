# -*- coding: utf-8 -*-

import click
import os
import pandas as pd


def file_split(file):
    s = file.split('.')
    name = '.'.join(s[:-1])  # get directory name
    return name


def getsheets(inputfile):
    name = file_split(inputfile)
    try:
        os.makedirs(name)
    except:
        pass

    df1 = pd.ExcelFile(inputfile)
    for x in df1.sheet_names:
        print(x + '.xlsx', 'Done!')
        df2 = pd.read_excel(inputfile, sheetname=x)
        filename = os.path.join(name, x + '.xlsx')
        df2.to_excel(filename, index=False)
    print('\nAll Done!')


def get_sheet_names(inputfile):
    df = pd.ExcelFile(inputfile)
    for i, flavor in enumerate(df.sheet_names):
        print('{0:>3}: {1}'.format(i + 1, flavor))


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-n', '--sheet-names', is_flag=True)
@click.argument('inputfile')
def cli(sheet_names, inputfile):
    '''Convert a Excel file with multiple sheets to several file with one sheet.

    Examples:

    \b
        getsheets filename

    \b
        getsheets -n filename
    '''
    if sheet_names:
        get_sheet_names(inputfile)
    else:
        getsheets(inputfile)


cli()
