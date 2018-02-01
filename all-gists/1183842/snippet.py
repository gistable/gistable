import sys
from java.io import *
import java.io.InputStream
import java.io.FileInputStream
import java.lang.String # blah....converting String types between Java/Python is tedious
sys.path.append("pdfbox-1.0.0.jar") # or wherever you stashed it
import org.apache.pdfbox

"""
This method merges the FileInputStreams that the streamList points to, into the
outputStream, which is saved to disk in place.
"""
def pdf_merger_utility_in_memory(streamList, outputStream):
    #need these two defined in order to use the PDFMergerUtility class
    destination = org.apache.pdfbox.pdmodel.PDDocument()
    source = org.apache.pdfbox.pdmodel.PDDocument()
    util = org.apache.pdfbox.util.PDFMergerUtility()
    # enforce a list length of 2 or more streams, otherwise merging is dumb.
    if(streamList is not None and len(streamList) > 1 ):
        try:
            #first stream in the list is the destination to append to
            destination = org.apache.pdfbox.pdmodel.PDDocument.load(streamList[0], True) #true tells it to skip corrupt files, I don't care about misses.
            print destination
            for x in xrange(1,len(streamList)):
                source = org.apache.pdfbox.pdmodel.PDDocument.load(streamList[x], True)
                print "stream loaded"
                print source
                try:
                    print type(destination), type(source)
                    util.appendDocument(destination, source)
                    source.close()
                    print "Appended successfully"
                except:
                    # I'm just ignoring the "did not close the pdf" error
                    # since this is a proof of concept.
                    instance = sys.exc_info()[1]
                    print instance
            destination.save(outputStream)
            print "Saved to outputStream"
        except:
            instance = sys.exc_info()[1]
            print instance

if __name__ == "__main__":
    #hard coded examples
    FILE_PATH_1 = java.lang.String("./UsabilityChecklists.pdf")
    FILE_PATH_2 = java.lang.String("./web.pdf")
    #convert java strings to java FISs
    file1 = java.io.FileInputStream(FILE_PATH_1)
    file2 = java.io.FileInputStream(FILE_PATH_2)
    files = (file1, file2)
    pdf_merger_utility_in_memory(files, "./merged_result.pdf")
    