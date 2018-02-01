#! /usr/bin/python
#
import sys
import os
import tempfile
from Quartz.CoreGraphics import *
from os.path import splitext
from os.path import basename
from os.path import join


def createPDFDocumentWithPath(path):
	return CGPDFDocumentCreateWithURL(CFURLCreateFromFileSystemRepresentation(kCFAllocatorDefault, path, len(path), False))

def main(argv):

	for input_pdf_filename in argv:
		doc = createPDFDocumentWithPath(input_pdf_filename)
		page_one = CGPDFDocumentGetPage(doc, 1)
		mediaBox = CGPDFPageGetBoxRect(page_one, kCGPDFMediaBox)
		if CGRectIsEmpty(mediaBox):
			mediaBox = None

		file_name, extension = splitext(basename(input_pdf_filename))
		output_path = join(tempfile.gettempdir(), file_name + "_page1" + extension)
		writeContext = CGPDFContextCreateWithURL(CFURLCreateFromFileSystemRepresentation(kCFAllocatorDefault, output_path, len(output_path), False), None, None)
		CGContextBeginPage(writeContext, mediaBox)
		CGContextDrawPDFPage(writeContext, page_one)
		CGContextEndPage(writeContext)
		CGPDFContextClose(writeContext)
		del writeContext

		print output_path


if __name__ == "__main__":
	main(sys.argv[1:])