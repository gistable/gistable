# -*- coding: utf-8 -*-
"""
Scrape a table from wikipedia using python. Allows for cells spanning multiple rows and/or columns. Outputs csv files for
each table
"""

from bs4 import BeautifulSoup
import urllib2
import os
import codecs
wiki = "https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart_for_English_dialects"
header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
req = urllib2.Request(wiki,headers=header)
page = urllib2.urlopen(req)
soup = BeautifulSoup(page)
 

tables = soup.findAll("table", { "class" : "wikitable" })

# show tables
for table in tables:
    print "###############"
    print table.text[:100]

for tn in range(len(tables)):
    table=tables[tn]

    # preinit list of lists
    rows=table.findAll("tr")
    row_lengths=[len(r.findAll(['th','td'])) for r in rows]
    ncols=max(row_lengths)
    nrows=len(rows)
    data=[]
    for i in range(nrows):
        rowD=[]
        for j in range(ncols):
            rowD.append('')
        data.append(rowD)
    
    # process html
    for i in range(len(rows)):
        row=rows[i]
        rowD=[]
        cells = row.findAll(["td","th"])
        for j in range(len(cells)):
            cell=cells[j]
            
            #lots of cells span cols and rows so lets deal with that
            cspan=int(cell.get('colspan',1))
            rspan=int(cell.get('rowspan',1))
            for k in range(rspan):
                for l in range(cspan):
                    data[i+k][j+l]+=cell.text
    
        data.append(rowD)
        
    # write data out
    
        page=os.path.split(wiki)[1]
    fname='output_{}_t{}.csv'.format(page,tn)
    f = codecs.open(fname, 'w')#,encoding='utf-8')
    for i in range(nrows):
        rowStr=','.join(data[i])
        rowStr=rowStr.replace('\n','')
        print rowStr
        rowStr=rowStr#.encode('unicode_escape')
        f.write(rowStr+'\n')      
        
        
    f.close()
        

    
