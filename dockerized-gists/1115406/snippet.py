#!/usr/bin/env python

import sys

if __name__ == '__main__' and len(sys.argv) > 5 and sys.argv[1][-3:].upper() == 'PDF':
  original = sys.argv[1]
  target   = original[:-4] + '.cropped.pdf'
  left     = int(sys.argv[2])
  top      = int(sys.argv[3])
  right    = int(sys.argv[4])
  bottom   = int(sys.argv[5])

  from pyPdf import PdfFileWriter, PdfFileReader
  pdf = PdfFileReader(file(original, 'rb'))
  out = PdfFileWriter()
  for page in pdf.pages:
    page.mediaBox.upperRight = (page.mediaBox.getUpperRight_x() - right, page.mediaBox.getUpperRight_y() - top)
    page.mediaBox.lowerLeft  = (page.mediaBox.getLowerLeft_x()  + left,  page.mediaBox.getLowerLeft_y()  + bottom)
    out.addPage(page)    
  ous = file(target, 'wb')
  out.write(ous)
  ous.close()

else:
  print 'EXAMPLE: pdfcrop.py original.pdf 20 30 20 40'
