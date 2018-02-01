# Thanks to http://stackoverflow.com/questions/9884353/xls-to-csv-convertor
import os, csv, xlrd

excel_file = '/path/to/file.xls'
#we're specifying a directory here because we'll have several files
csv_filepath = 'path/to/csv/directory'

def csv_from_excel(excel_file):
    workbook = xlrd.open_workbook(excel_file)
    all_worksheets = workbook.sheet_names()
  
    for worksheet_name in all_worksheets:
        worksheet = workbook.sheet_by_name(worksheet_name)
        your_csv_file = open(''.join([csv_filepath,worksheet_name,'.csv']), 'wb')
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
        
        for rownum in xrange(worksheet.nrows):
            wr.writerow([unicode(entry).encode("utf-8") for entry in worksheet.row_values(rownum)])
        your_csv_file.close()
  
csv_from_excel(excel_file)