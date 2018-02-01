import itertools

from openpyxl.reader.excel import load_workbook

def getrows(sheet, cols):
    headers = [c.value for c in sheet.rows[0] if c.value]
    for row in sheet.rows[1:]:
        d = dict(zip(headers, [c.value for c in row]))
        yield dict((k2, d[k1]) for k1,k2 in cols)
        
def main():

    infile = sys.argv[1]
    wb = load_workbook(infile)
    lab = wb.get_sheet_by_name('Laboratory')
    
    keep = [
        (u'Order #','order_id'),
        (u'Activity Sub Type','activity_subtype'),
        (u'PROD name','prod_name'),
        (u'Alias','alias'),
        (u'Legal Description','legal_desc'),
        (u'Common Name','common_name'),
        (u'Alternate Name (Direct Care Provider Synonym)','alt_name'),
        (u'Alternate Name 2','alt_name2'),
        ]

    rows = getrows(lab, keep)
    
if __name__ == '__main__':
    main()
