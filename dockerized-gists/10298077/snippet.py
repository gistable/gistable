# code to take a PDF and scrape address information. Note that this particular script will
# only work using the specific PDF formatting my PDF had so you can use as a guide but
# it will definitely not work on your PDF!


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import re
import csv
import time

# thanks to this source for pdfminer code
#http://davidmburke.com/2014/02/04/python-convert-documents-doc-docx-odt-pdf-to-plain-text-without-libreoffice/


path ="xxx.pdf"
outpath = "xxx.csv"


time1 = time.time()
alltext = convert_pdf_to_html(path)
time2 = time.time()
print time2-time1




pattern = '(?<=<span style="font-family: UQGGBU\+GaramondPremrPro-LtDisp; font-size:12px">)(.*?)(?=<br></span></div>)'
createDirectory(alltext, outpath, pattern)


def convert_pdf_to_html(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0 #is for all
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str


def getresult(theinfo):
    if theinfo:
        theinfo = theinfo.group(0)
    else:
        theinfo = ''
    return theinfo


def createDirectory(instring, outpath, split_program_pattern):
    i = 1
    with open(outpath, 'wb') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',' , quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # write the header row
        filewriter.writerow(['programname', 'address', 'addressxtra1', 'addressxtra2', 'city', 'state', 'zip', 'phone', 'altphone', 'codes'])

        # cycle through the programs
        for programinfo in re.finditer(split_program_pattern, instring,  re.DOTALL):
            print i
            i=i+1

            # pull out the pieces
            programname = getresult(re.search('^(?!<br>).*(?=\\n)', programinfo.group(0)))
            programname = re.escape(programname) # some facilities have odd characters in the name

            # there are a lot of different formats for 'address'
            addressBegNum ='((?<=>)(\s{0,})\d{1,}[\w\s-]+(?=\\n))'
            addressAltNum = '(?<=>)([\w\s]+)(Avenue|Street|Way|Road|Boulevard|Way|Highway|Cutoff)([\w\s]{0,})(?=\\n)'
            addressPOBox = '(?<=>)([\w\s]{0,})P\.O\. Box.*?(?=\\n)'
            address  =getresult(re.search(addressBegNum + '|' + addressAltNum + '|' + addressPOBox, programinfo.group(0)))
            if address: address = re.escape(address)

            citystatezip  =getresult(re.search('(?<=>)([a-zA-Z\s]+, [a-zA-Z\s]{2} \d{5,10})(?=\\n)', programinfo.group(0)))
            mainphone  =getresult(re.search('(?<=<br>)\(\d{3}\) \d{3}-\d{4}x{0,1}\d{0,}(?=\\n)', programinfo.group(0)))
            altphones = re.findall('(?<=<br>)[a-zA-Z\s]+: \(\d{3}\) \d{3}-\d{4}x{0,1}\d{0,}(?=\\n)(?=\\n)', programinfo.group(0))
            codes =re.search('(?<=>)(\s{0,1})([A-Z]{1})([A-Z]{1}|\d{1,2})(\\n|([-\s]{1,})(\\n|<|([A-Z]{1})([A-Z]{1}|\d{1,2}))).*', programinfo.group(0), re.DOTALL)

            # for altphones, we don't need to save them in different fields so just
            # join them with a semi colon
            if altphones != '':
                altphones = '; '.join(altphones)

            # codes are messy, clean them up
            if codes:
                #if programname[0:6] == 'Riverb': blah = codes
                codes = re.sub('</span>', ',', codes.group(0))
                codes = re.sub('<.*?>', '', codes)# drop everything between <>
                codes = re.sub(' , ', ', ', codes)# replace spaces associated with commas with just comma
                codes = re.sub('s', '', codes)
                codes = re.sub(',,', ',', codes)
                codes = re.sub('\n', '', codes)

            # BEGIN TRYING TO PULL OUT ADDITIONAL INFORMATION IN THE ADDRESS LIKE
            # SUITE NAME ETC

            # If we have a program name and an address call 'altinfo1' the line,
            # if it exists, between them
            if (programname != '') & (address != ''):
                altinfo1 = re.search('(?<=' + programname + ').*(?=' + address + '\\n)', programinfo.group(0), re.DOTALL)

                if altinfo1:
                    altinfo1 = re.sub('<.*>|\\n', '', altinfo1.group(0))
                else:
                    altinfo1 = ''

            # If we have a address and a citystatezip call 'altinfo2' the line,
            # if it exists, between them
            if (address != '') & (citystatezip != ''):
                altinfo2 = re.search('(?<=' + address + ').*(?=' + citystatezip + '\\n)', programinfo.group(0), re.DOTALL)

                if altinfo2:
                    altinfo2 = re.sub('<.*>|\\n', '', altinfo2.group(0))
                else:
                    altinfo2 = ''

            # If we DO NOT have an a. In ddress but we do have citystatezip then pull
            # out altinfo1 and altinfo2 if they exist.
            if (address == '') & (citystatezip != ''):
                altinfoTmp = re.search('(?<=' + programname + ').*(?=' + citystatezip + '\\n)', testing, re.DOTALL)
                altinfo1 = ''
                altinfo2 = ''
                if altinfoTmp:
                    altinfoTmp = re.sub('<.*>', '', altinfoTmp.group(0))
                    altinfoTmp = altinfoTmp.strip().splitlines()
                    n = len(altinfoTmp)
                    altinfo1 = altinfoTmp[0]
                    if n==2:
                        altinfo2 = altinfoTmp[1]
                    if n>2:
                        altinfo2 = '; '.join(altinfoTmp.pop(0))

            # Probably this could have been done more simply but basically
            # if an element does not exist set it to empty
            if 'altinfo1' not in locals(): altinfo1=''
            if 'altinfo2' not in locals(): altinfo2=''
            if 'mainphone' not in locals(): mainphone=''
            if 'altphones' not in locals(): altphones=''
            if 'codes' not in locals(): codes=''

            # since we escaped the program name we need to unescape
            if 'programname' in locals():  programname = re.sub(r'\\(.)', r'\1', programname)

            # since we escaped the address we need to unescape
            if 'address' in locals():
                address = re.sub(r'\\(.)', r'\1', address)
            else:
                address = ''

            # last minute I decided to split up the citystatezip
            if citystatezip:
                citystatezip = citystatezip.split(',')
                city=citystatezip[0]
                state = citystatezip[1].lstrip().split(' ')[0]
                zip = citystatezip[1].lstrip().split(' ')[1]
            else:
                city=''
                state=''
                zip=''

            # write then delete the elements
            finline = [programname,address,altinfo1, altinfo2 ,city, state, zip, mainphone, altphones, codes]
            del programname, altinfo1, altinfo2, address, citystatezip, mainphone, altphones, codes, addressBegNum, addressAltNum, city, state, zip

            filewriter.writerow(finline)