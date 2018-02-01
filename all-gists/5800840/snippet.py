
# 1. Add some necessary libraries
import scraperwiki
import urllib2, lxml.etree

# 2. The URL/web address where we can find the PDF we want to scrape
url = 'http://cdn.varner.eu/cdn-1ce36b6442a6146/Global/Varner/CSR/Downloads_CSR/Fabrikklister_VarnerGruppen_2013.pdf'

# 3. Grab the file and convert it to an XML document we can work with
pdfdata = urllib2.urlopen(url).read()
xmldata = scraperwiki.pdftoxml(pdfdata)
root = lxml.etree.fromstring(xmldata)

# 4. Have a peek at the XML (click the "more" link in the Console to preview it).
print lxml.etree.tostring(root, pretty_print=True)

# 5. How many pages in the PDF document?
pages = list(root)
print "There are",len(pages),"pages"

'''
# 6. Iterate through the elements in each page, and preview them
for page in pages:
    for el in page:
        if el.tag == "text":
            print el.text, el.attrib

# REPLACE STEP 6 WITH THE FOLLOWING
# 7. We can use the positioning attibutes in the XML data to help us regenerate the rows and columns
for page in pages:
    for el in page:
        if el.tag == "text":
            if int(el.attrib['left']) < 100: print 'Country:', el.text,
            elif int(el.attrib['left']) < 250: print 'Factory name:', el.text,
            elif int(el.attrib['left']) < 500: print 'Address:', el.text,
            elif int(el.attrib['left']) < 1000: print 'City:', el.text,
            else:
                print 'Region:', el.text

# REPLACE STEP 7 WITH THE FOLLOWING
# 8. Rather than just printing out the data, we can generate and display a data structure representing each row.
#    We can also skip the first page, the title page that doesn't contain any of the tabulated information we're after.
for page in pages[1:]:
    for el in page:
        if el.tag == "text":
            if int(el.attrib['left']) < 100: data = { 'Country': el.text }
            elif int(el.attrib['left']) < 250: data['Factory name'] = el.text
            elif int(el.attrib['left']) < 500: data['Address'] = el.text
            elif int(el.attrib['left']) < 1000: data['City'] = el.text
            else:
                data['Region'] = el.text
                print data

# REPLACE STEP 8 WITH THE FOLLOWING
# 9. This really crude hack ignores data values that correspond to column headers.
#    A more elecgant solution would use ignore elements in the first table row on each page.
skiplist=['COUNTRY','FACTORY NAME','ADDRESS','CITY','REGION']
for page in pages[1:]:
    for el in page:
        if el.tag == "text" and el.text not in skiplist:
            if int(el.attrib['left']) < 100: data = { 'Country': el.text }
            elif int(el.attrib['left']) < 250: data['Factory name'] = el.text
            elif int(el.attrib['left']) < 500: data['Address'] = el.text
            elif int(el.attrib['left']) < 1000: data['City'] = el.text
            else:
                data['Region'] = el.text
                print data

# REPLACE STEP 9 WITH THE FOLLOWING
# 10. A crude way of adding data o the database - write each row as we scrape it.
skiplist=['COUNTRY','FACTORY NAME','ADDRESS','CITY','REGION']
for page in pages[1:]:
    for el in page:
        if el.tag == "text" and el.text not in skiplist:
            if int(el.attrib['left']) < 100: data = { 'Country': el.text }
            elif int(el.attrib['left']) < 250: data['Factory name'] = el.text
            elif int(el.attrib['left']) < 500: data['Address'] = el.text
            elif int(el.attrib['left']) < 1000: data['City'] = el.text
            else:
                data['Region'] = el.text
                print data
                scraperwiki.sqlite.save(unique_keys=[], table_name='fabvarn', data=data)

# REPLACE STEP 10 WITH THE FOLLOWING
# 11. A more efficient way of writing to the database might be to write all the records scraped from a page one page at a time.
skiplist=['COUNTRY','FACTORY NAME','ADDRESS','CITY','REGION']
bigdata=[]
for page in pages[1:]:
    for el in page:
        if el.tag == "text" and el.text not in skiplist:
            if int(el.attrib['left']) < 100: data = { 'Country': el.text }
            elif int(el.attrib['left']) < 250: data['Factory name'] = el.text
            elif int(el.attrib['left']) < 500: data['Address'] = el.text
            elif int(el.attrib['left']) < 1000: data['City'] = el.text
            else:
                data['Region'] = el.text
                print data
                bigdata.append( data.copy() )
    scraperwiki.sqlite.save(unique_keys=[], table_name='fabvarn', data=bigdata)
    bigdata=[]

'''
# REPLACE STEP 11 WITH THE FOLLOWING
# 12. If necessary, and becuase we are unsing incremental rather than repeat keys,
#     we may need to clear the database table before we right to it.
#     A utulity function can help us do that.

def dropper(table):
    if table!='':
        try: scraperwiki.sqlite.execute('drop table "'+table+'"')
        except: pass

dropper('fabvarn')

skiplist=['COUNTRY','FACTORY NAME','ADDRESS','CITY','REGION']
bigdata=[]
for page in pages[1:]:
    for el in page:
        if el.tag == "text" and el.text not in skiplist:
            if int(el.attrib['left']) < 100: data = { 'Country': el.text }
            elif int(el.attrib['left']) < 250: data['Factory name'] = el.text
            elif int(el.attrib['left']) < 500: data['Address'] = el.text
            elif int(el.attrib['left']) < 1000: data['City'] = el.text
            else:
                data['Region'] = el.text
                print data
                bigdata.append( data.copy() )
    scraperwiki.sqlite.save(unique_keys=[], table_name='fabvarn', data=bigdata)
    bigdata=[]'''