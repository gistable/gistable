'''
Text from Searchable pdfs
Scrape Text off Wisconsin Ads pdfs

Uses pyPdf to get text from searchable pdfs. The script is for tailored for getting data 
from Wisconsin Political Ads Database: http://wiscadproject.wisc.edu/Storyboards.

@author: Gaurav Sood

Created on November 02, 2011
'''

import sys, os, re, pyPdf, codecs, csv, string

def convertPdf2String(pdfFile):
      content = ""
      # try catch for EOF exception - which seems like a nuisance exception
      try:
          # load PDF file
          pdf = pyPdf.PdfFileReader(file(pdfFile, "rb"))
          # iterate pages
          for i in range(0, pdf.getNumPages()):
              # extract the text from each page
              content += pdf.getPage(i).extractText() + " \n"
              # collapse whitespaces
              content = u" ".join(content.replace(u"\xa0", u" ").strip().split())
      except Exception, e:
        return "Unable to open file: %s with error: %s" % (pdfFile, str(e))
      return content

def writer(path, out):
    dirList=os.listdir(path)
    for fname in dirList: 
        row = convertPdf2String(path+fname).encode("ascii", "xmlcharrefreplace")
        print row
        if row.find('Brand') > 0:
            title = ' '.join(row.split(' ')[1:]).partition('Brand:')[0]
            creative = row.partition('Brand:')[0]
            brand = row.partition('Brand:')[2].partition('Parent')[0]
        else:
            continue
        race = row.split(' ')[0]  
        parent =row.partition('Parent:')[2].partition('Aired:')[0]
        date = row.partition('Aired:')[2].partition('Creative Id:')[0].strip()
        creative_id = row.partition('Creative Id:')[2].partition('[')[0]
        sponsor=""
        if row.find('[PFB'):
            text = '['+row.partition('Creative Id:')[2].partition('[')[2].partition('[PFB')[0]
            sponsor = row.partition('[PFB')[2]
        if len(sponsor.split(':')) == 1: 
            sponsor = sponsor.split(':')[0].rstrip()   
        else:
            sponsor = sponsor.split(':')[1].rstrip()
        if sponsor.find('Copyright'):
            sponsor = sponsor.partition('Copyright')[0].lstrip()
        if sponsor.find(']'):
            sponsor = sponsor.partition(']')[0]        
        #Clean if you want to
        text = re.sub("Copyright 2003 TNS Media Intelligence/CMAG www.PoliticsOnTV.com 1-866-559-CMAG", "", text)
        text = re.sub("Copyright 2004 TNS Media Intelligence/CMAG www.PoliticsOnTV.com 1-866-559-CMAG", "", text)
        text = re.sub("Storyboard", "", text)
        
        record = (creative, creative_id, date, race, title, brand, parent, sponsor,text)
        out.writerow(record)

# Header Row
header = ('creative', 'creative_id','date.aired', 'race', 'title', 'brand', 'parent', 'sponsor', 'text')
    
ads = csv.writer(open('outpath', 'wb'))
ads.writerow(header) # Header Row
writer(path.to.ads.folder, ads)