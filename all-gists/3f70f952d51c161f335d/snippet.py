#!/usr/bin/python3
# -*- coding: utf-8 -*-
# tax.py   written by Duncan Murray 14/7/2015
#
# Step 1 - download all your bank statements in CSV format
#          then update the raw_files dictionary below
#
# Step 2 - create a mappings.csv file which maps the start of a
#          a details column to a mapping, e.g.
# Details_string	        Maps_to	            Deductible
# cc t'fer	                Bank Fees	        N
# VISA-ASIC	                Business Renewal	Y
# Wdl ATM CBA ATM	          Cash Withdrawal	  N
# MSY TECHNOLOGY SA	        Computer	        Y
# VISA-STEAMGAMES.COM       Entertainment	    N
# Debit Adjustment	        Fee	              N
#
# Step 3 - run this program which concatenates your bank statements
#          and adds categories for each mapping line

raw_files = [
    {'name':'Comm_keycard', 'src':'Comm', 'fname':'CSVData_Comm_Keycard.csv'},
    {'name':'Comm_maincard', 'src':'Comm', 'fname':'CSVData_Comm_Maincard.csv'},
    {'name':'CPS_S1', 'src':'CPS', 'fname':'StatementCsv_S1.csv'},
    {'name':'CPS_S2', 'src':'CPS', 'fname':'StatementCsv_S2.csv'},
    ]

def main():
    map = read_mappings('mappings.csv')
    dat = read_csv(map)
    save_data(dat)
 
def save_data(dat):
    """
    save the combined files as CSV
    """
    with open('bank_statements_2015_2016.csv', 'w') as f:
        f.write('src,date,amount,details,balance,type,category,is_deductible,is_income\n')
        for row in dat:
            for col in row:
                if type(col) is str:
                    f.write(col + ', ')
                else:
                    f.write(str(col) + ', ')
            f.write('\n')
        
def read_csv(m):
    lst = []
    for fd in raw_files:
        with open(fd['fname'], 'r') as f:
            for num, line in enumerate(f):
                if line[0:28] == 'Effective Date,Entered Date,':
                    pass
                else:
                    dte, amt, det, cat = extract_cols(fd, line)
                    cat1, cat2, is_ded, is_inc = get_tax_cat(line, amt, det, m)
                    lst.append([fd['src'], dte, amt, det, cat, cat1, cat2, is_ded, is_inc])
    return lst
    
def get_tax_cat(line, amount, det, m):
    """
    takes a list of mappings 'm' and uses this to 
    get a category
    """
    cat_broad = 'Expense'
    cat_narrow = ''
    is_deductable = False
    is_income = False
    if amount > 0:
        is_income = True
        cat_broad = 'Income'
    for map_line in m:
        map_str = map_line[0][0].strip() + ' '
        tst_str = det[0:len(map_str)].strip() + ' '
        if tst_str == map_str: 
            cat_narrow = map_line[0][1]
    return cat_broad, cat_narrow, is_deductable, is_income
    
    
def extract_cols(fd, line):
    """
    parses the columns from 2 sources into a standard form
    You will need to modify this if your bank has different
    formats.
    Column Headers:
    CSVData_Comm_Keycard = date,amount,details
    CSVData_Comm_Maincard = date,amount,details
    StatementCsv_S1 = Effective Date,Entered Date,Transaction Description,Amount,Balance
    StatementCsv_S2 = Effective Date,Entered Date,Transaction Description,Amount,Balance
    """
    dte = ''
    amt = 0 
    det = ''
    cat = ''
    cols = line.split(',')
    if fd['src'] == 'Comm':
        dte = cols[0].strip('"').strip()
        amt = float(cols[1].strip('"').strip() )
        det = cols[2].strip('"').strip()
        cat = cols[3].strip('"').strip()
    elif fd['src'] == 'CPS':    
        dte = cols[1].strip('"').strip()
        amt = float(cols[3].strip('"').strip())
        det = cols[2].strip('"').strip()
    return dte, amt, det, cat

def read_mappings(fname):
    """
    read a mapping file to see how to map details. Format is 
    Details_string	      Maps_to	            Deductible
    cc t'fer	            Bank Fees	          N
    VISA-ASIC	            Business Renewal	  Y
    Wdl ATM CBA ATM	      Cash Withdrawal	    N
    """
    maps = []
    with open(fname, 'r') as f:
        for line in f:
            if line.strip() != ',,':
                cols = line.split(',')
                maps.append([cols])
    return maps
    
main()    