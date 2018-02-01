from lxml import etree
import csv
#Inspired by http://www.blog.pythonlibrary.org/2010/11/20/python-parsing-xml-with-lxml/
#----------------------------------------------------------------------
def parseMOSAIC_Level1_XML(xmlFile,writer):
	context = etree.iterparse(xmlFile)
	record = {}
	records = []
	print 'starting...'
	for action, elem in context:
		if elem.tag=='useRecord' and action=='end':
			#if record !={}: records.append(record)
			if 'ucasCode' in record and 'localID' in record:
				for cc in record['ucasCode']:
					writer.writerow([record['localID'],cc])
			record={}
		if elem.tag=='localID':
			record['localID']=elem.text
		elif elem.tag=='courseCode' and 'type' in elem.attrib and elem.attrib['type']=='ucas':
			if 'ucasCode' not in record:
				record['ucasCode']=[]
			record['ucasCode'].append(elem.text)
		elif elem.tag=='progression' and elem.text=='staff':
			record['staff']='staff'
		#print action,':',elem.tag
	#return records


writer = csv.writer(open("test.csv", "wb"))

#http://library.hud.ac.uk/wikis/mosaic/index.php/Project_Data
f='mosaic.2008.level1.1265378452.0000001.xml'
s='mosaic.2008.sampledata.xml'
parseMOSAIC_Level1_XML(f,writer)