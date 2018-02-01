'''
@desc Parse Google Drive spreadsheet data via python
@author Misha M.-Kupriyanov https://plus.google.com/104512463398531242371/
@link https://gist.github.com/3969255
'''
# Spreadsheet https://docs.google.com/spreadsheet/pub?key=0Akgh73WhU1qHdFg4UmRhaThfUFNBaFR3N3BMVW9uZmc&output=html


import logging
import urllib2
import json

def getRowValue(row, format, column_name):
    logging.info('getRowValue[%s]:%s' % (column_name, row))
    
    if str(column_name) == '':
        raise ValueError('column_name must not empty')
        
    begin = row.find('%s:' % column_name)
    
    logging.info('begin:%s' % begin)
       
    if begin == -1:
        return ''
    
    begin = begin + len(column_name) + 1
    
       
    end = -1
    found_begin = False
    
    for entity in format:
        logging.info('checking:%s' % entity)
        
        if found_begin and row.find(entity) != -1:
            end = row.find(entity)
            break
        
        if entity == column_name:
            found_begin = True
    
    
    #check if last element
    if format[len(format) -1 ] == column_name:
        end = len(row)
    else:
        if end == -1:
            end = len(row)
        else:
            end = end - 2
        
    logging.info('%s:%s' % (column_name, row) )
    #logging.info('speakertitle[%s]' % speaker_title )
    #logging.info('%s:%s' % (column_name, row.find(column_name)))
#        logging.info('%s - %s' % (begin, end))
    
    value = row[begin: end].strip()
    
    logging.info('%s[%s-%s]:[%s]' % (column_name, begin, end, value))
    

    return value


# JSON Representation
url = 'https://spreadsheets.google.com/feeds/list/0Akgh73WhU1qHdFg4UmRhaThfUFNBaFR3N3BMVW9uZmc/od6/public/basic?prettyprint=true&alt=json';

response = urllib2.urlopen(url)
html = response.read()
html = json.loads(html)

format = ['column1', 'column2', 'column3']     

for entry in html['feed']['entry']:
	row = entry['content']['$t'].encode('utf-8').strip()
            
        column1 = column2 = column3 = ''

	column1 = getRowValue(row, format, 'column1')
	column2 = getRowValue(row, format, 'column2')
	column3 = getRowValue(row, format, 'column3')

	print 'column1:%s column2:%s column3:%s' % (column1, column2, column3)	




