import os
from docx import Document
import uuid

def getDocList(rootFoldr):
    filelst = []

    for(dirpath, _, files) in os.walk(rootFoldr):
        for filename in files:
            filepath = os.path.join(dirpath, filename)
            filelst.append(filepath)
    return (filelst)


def convertToDocx(rootFoldr):
    flst = getDocList(rootFoldr)

    for each_file in flst:
        #each_file.encode('utf-8')
        with open(each_file, 'r') as rdcontent:
            xdoc = Document()
            xdoc.add_paragraph('{}'.format(rdcontent.readlines()))
            xdoc.save('{}/{}.docx'.format(os.path.dirname(os.path.realpath(each_file)),uuid.uuid4()))
            print ("{}  converted to docx".format(each_file))

convertToDocx('data/')
