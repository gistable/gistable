import csv
#import sys

from xml.etree import ElementTree
from xml.dom import minidom

csvFileName = "Distribuidoras.csv"
xmlFileName = "distribuidoras.xml"

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


with open(csvFileName, 'rU') as csvFile:
    #reader = csv.reader(csvFile, delimiter=';')
    reader = unicode_csv_reader(csvFile, delimiter=';')
    
    comercializadoras_tag = ElementTree.Element('distribuidoras')
    for row in reader:
		#print row
		
		if(row[0]!='' or row[1]!='' or row[2]!='' or row[3]!='' or row[4] or row[5]!='' or row[6]!=''):
			attrs = {'name': row[0],
					 'tel': row[1],
					 'cif': row[2],
					 'direccion': row[3],
					 'codigo': row[4],
					 'division': row[5],
					 'zona': row[6]
					}
			#print attrs
					
			ElementTree.SubElement(comercializadoras_tag, 'distribuidora', attrib=attrs)
        
    resultXML =  minidom.parseString(ElementTree.tostring(comercializadoras_tag)).toprettyxml()
    resultXML_utf8 = resultXML.encode('UTF-8')
    #print resultXML_utf8
	
    with open(xmlFileName, 'w+') as xmlFile:
	    xmlFile.write(resultXML_utf8)
	