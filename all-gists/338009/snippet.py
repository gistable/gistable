#!/usr/bin/python
# -*- coding: utf-8 -*-

# pydftk
# Copyright 2009 W. Kyle White
# Rewrite of stapler; Copyright 2009 Philip Stark
#   original stapler license is found in the file "LICENSE"
#   if this file is missing, you can find a copy at
#   http://stuff.codechaos.ch/stapler_license
# Features added:
#   code cleanup and restructure
#   added col and zip: collate pages from selection (file1p1, file2p1, file1p2, file2p2...)
#   replace filename with "-" to use stdin or stdout. selects based on context
#   can use page ranges for all modes (including cat and burst) (this makes cat function the same as sel)
#   if no page range is given for a file, all pages are assumed
#   increased page range options
#      "end" is replaced with the number of last page
#      reverse ordering allowed, e.g. 3-1 returns the pages 3, 2, 1
#      append "e" for even, "o" for odd, e.g. 1-5o returns 1, 3, 5
#      append x# for each # page, e.g. 1-7x3 returns 1,4,7
#      append :(command) to rotate pages, command can be r,l,u,d,cw#,ccw#. cw and ccw can take # in multiple of 90 degrees
#   all modes now have optional printf formatted output name:
#      split/burst: %n filename, %e extension, %i printf formatted iterator, %p printf formated pagenumber (use %0p for stapler formatted)
#       all others: %n or %1n for first input filename, %2n for second... same for %e extensions, no %p or %i allowed
#   verbose mode disabled by default, add -v to commandline to enable, -q to disable
#   -p=(password) following an input file to decrypt file with (password)
#   -u=(password) set user password for output
#   -o=(password) set owner password for output
#   lots of bugs have been added and well hidden? :)
#
# Todo:
#   add N-up to sel/cat
#   possibly remove duplicate modes?
#   add watermark/merge page
#   add attach/extract files
#   add metadata reading/manipulation
#   add render PDF<>Image
#   add extract embedded object
#
# --Feature comparison to pdftk: *added, +todo
#  *Merge PDF Documents
#  *Split PDF Pages into a New Document
#  *Rotate PDF Pages or Documents
#  *Decrypt Input as Necessary (Password Required)
#  *Encrypt Output as Desired
#   Fill PDF Forms with FDF Data or XFDF Data and/or Flatten Forms
#  +Apply a Background Watermark or a Foreground Stamp
#   Report on PDF Metrics such as Metadata, Bookmarks, and Page Labels
#  +Update PDF Metadata
#  +Attach Files to PDF Pages or the PDF Document
#  +Unpack PDF Attachments
#  *Burst a PDF Document into Single Pages
#  +Uncompress and Re-Compress Page Streams
#   Repair Corrupted PDF (Where Possible)






import math
from pyPdf import PdfFileWriter, PdfFileReader
import sys
import re
import os.path
from StringIO import StringIO

#######################################################################################################
# bufferstdin and bufferstdout are needed to add functions to stdin and stdout to be usable for pyPdf #
# sys.stdout.write(self.getvalue()) can be used in close() instead of sys.stdout.write in write()     #
#######################################################################################################
class bufferstdin(StringIO):
    name = "<stdin>"
    def __init__(self):
        StringIO.__init__(self, sys.stdin.read())
class bufferstdout(StringIO):
    name = "<stdout>"
    def write(self,buffer):
        sys.stdout.write(buffer)
        StringIO.write(self,buffer)
    def close(self):
#        sys.stdout.write(self.getvalue())
        sys.stdout.flush()
        sys.stdout.close()
        StringIO.close(self)
###### end class definitions ######
###################################


##################################################
# Handle all command line arguments and dispatch #
##################################################
verbose = False
ownerpassword=""
userpassword=""


def parse_args(argv):
    global verbose
    global ownerpassword
    global userpassword

    mode = ""
    # Possible modes are:
    # cat,sel     - concatenate multiple PDFs
    # del         - delete single pages or ranges (opposite of sel)
    # col,zip     - collate PDFs
    # split,burst - split a pdf into single pages
    modes = ["cat", "col", "burst", "split", "del", "sel", "zip"]

    if (len(argv) < 3):
        sys.stderr.write( "too few arguments" )
        halp()
        sys.exit(0)
    
    if argv[1] in ["-h", "--help"]:
        halp()
        sys.exit(0)
    

    mode = argv[1]
    files = argv[2:]


    if (not mode in modes):
        sys.stderr.write( "please input a valid mode" )
        halp()
        sys.exit()

    if ("-v" in files):
        verbose = True
        files.remove("-v")
    if ("-q" in files):
        verbose = False
        files.remove("-q") 

    ###### disable verbose if outputting to <stdout> ######
    if (mode not in ["burst", "split"] and files[-1] == "-"):
        verbose = False
        
    if verbose: print "mode: "+mode

    #burst/split does not require an output argument, if none is given then add the default
    if (mode in ["burst", "split"]) and not "%" in files[-1]:
        files += ["%np%0p.%e"]

    infilelist=[]
    pages=[]
    for argument in files[:-1]:

        if re.match('.*?\.pdf', argument) or argument =="-":
            infilelist.append(openpdf(argument,"in"))
            pages.append([])
        elif(re.match("^-p=.*", argument)):
            password=argument.replace("-p=","")
            if verbose: print "Decrypting " + infilelist[-1].stream.name + " with password \"" + password + "\""
            infilelist[-1].decrypt(password)
        elif(re.match("^-u=.*", argument)):
            password=argument.replace("-u=","")
            if verbose: print "!!Setting USER password to: " + "\"" + password + "\""
            userpassword=password
        elif(re.match("^-o=.*", argument)):
            password=argument.replace("-o=","")
            if verbose: print "!!Setting OWNER password to: " + "\"" + password + "\""
            ownerpassword=password            
        else:
            pages[len(infilelist)-1] += [argument]

    if (mode in ["burst", "split"]):
        burst(zip(infilelist, pages), files[-1])
    elif (mode in ["cat","sel"]):
        concatenate(zip(infilelist, pages), files[-1], inverse=False)
    elif (mode == "del"):
        concatenate(zip(infilelist, pages), files[-1], inverse=True)
    elif (mode in ["col","zip"]):
        collate(zip(infilelist, pages), files[-1])
###### end function parse_args ######
#####################################

#################################
# functions to process input    #
#################################
###### getpagequeue accepts a list of string arguments, and a list of tuple replacements
###### returns a list of tuples (page number, rotation angle) 1 per page
def getpagequeue(arguments, replacements):
    pagequeue = []
    if not arguments: arguments = ["1-end"]
    for argument in arguments:
        for i in range(len(replacements)):
            argument=argument.replace(replacements[i][0], replacements[i][1])

        pagerange=re.search('^[0-9]+(-[0-9]+)?', argument).group()
        modifiers=argument.replace(pagerange, "")

        select = (lambda x: True)
        selectarg=re.search('[eo]|(x[0-9]*)',modifiers)
        if selectarg:
            selectarg=selectarg.group()
            modifiers=modifiers.replace(selectarg,"")
            selecttests=dict([("e",(lambda x: not int(x)%2)), ("o",(lambda x: int(x)%2) )])
            if selectarg in selecttests.keys():
                select = selecttests[selectarg]
            else:
                skipcount=int(selectarg.replace("x",""))
                select = (lambda x, skipcount=skipcount: not (x-begin)%skipcount)

        angle = 0
        rotateflag=':'
        rotatearg=re.search(rotateflag+'[rlud]',modifiers)
        if rotatearg:
            print rotatearg.group()
            rotatearg=rotatearg.group().replace(rotateflag,"")
            rotateangle=dict([("u",0), ("d",180), ("l",-90), ("r",90)])
            if rotatearg in rotateangle.keys():
                angle=rotateangle[rotatearg]
                modifiers=modifiers.replace(rotateflag+rotatearg,"")

        rotatearg=re.search(rotateflag+'(c?cw[0-9]*)',modifiers)
        if rotatearg:
            rotatearg=rotatearg.group().replace(rotateflag,"")
            if "ccw" in rotatearg:
                angle=-int(rotatearg.replace("ccw",""))
                modifiers=modifiers.replace(rotateflag+rotatearg,"") #we know that rotatearg is all of ccw command
            elif "cw" in rotatearg:                
                angle=int(rotatearg.replace("cw",""))
                modifiers=modifiers.replace(rotateflag+rotatearg,"") #we know that rotatearg is all of cw command
        
        if re.search('^[0-9]+-[0-9]+$',pagerange):
            ###set up tests for even, odd, or none

            (begin,sep,end) = pagerange.partition("-")
            begin=int(begin)
            end=int(end)
            if begin < end:
                pagelist = filter(select,range(begin, end+1))
            else:
                pagelist = filter(select,range(end, begin+1))
                pagelist.reverse()
            for pageout in pagelist:
                if (select(pageout)):
                    pagequeue += [(pageout,angle)]
        elif re.search('^[0-9]+$',pagerange):
            pagequeue += [(int(pagerange),angle)]
        else:
            sys.stderr.write( "error: misformat for pagelist at \"" + inputname + "\"... exiting now" )
            sys.exit()
    return pagequeue
###### end function getpagequeue ######

###### openpdf accepts a filename string (or '-'), a string "in", "r", "rb" or "out", "w", "wb"
###### returns a PdfFileReader or file, directs to <stdin> or <stdout> for '-'
def openpdf(infilename, inout):
    global verbose
    pdf = []
    buf = []
    if inout in ["in","r","rb"]:
        if infilename == "-":
            buf=bufferstdin()
        elif os.path.exists(infilename):
            buf=file(infilename, "rb")
        else:
            sys.stderr.write( "error: " + infilename + " does not exist... exiting now" )
            sys.exit(2)
        if verbose: print "**Opening: " + infilename
        try:
            pdf = PdfFileReader(buf)
        except:
            sys.stderr.write( "Error opening " + buf.name)
            sys.exit(2) # pdf file is no pdf file...

    elif inout in ["out","w","wb"]:
        if infilename == "-":
            pdf = bufferstdout()
        else:
            if not os.path.exists(infilename):
                pdf = file(infilename, "wb")
            else:
                sys.stderr.write( "error: "+ filename +" already exists... exiting now")
                sys.exit(2)
    return pdf
###### end function openpdf ######
##################################

##################################################
# functions which process input and output files #
##################################################

###### burst accepts a list of (PdfFileReader, [string pageselect]), string outfileformat
###### returns nothing, splits pdf into selected pages and writes to pdfs
def burst(inpdfargs, outfileformat):
    global verbose
    global ownerpassword
    global userpassword

    i=0
    j=0
    for pdf, args in inpdfargs:

        numpages=pdf.getNumPages()
        replacements=[["end",str(numpages)]]
        pagequeue = getpagequeue( args, replacements)
        if verbose: print "**Processing: " + pdf.stream.name

        log10pages = int(math.ceil(math.log10(numpages)))
        (name, dot, ext) = pdf.stream.name.rpartition(".")

        for pageitem in pagequeue:
            page, angle = pageitem
            if ( (page <= numpages) and (page > 0)):
                output = PdfFileWriter()
                if userpassword or ownerpassword:
                    output.encrypt(userpassword,ownerpassword)
                output.addPage(pdf.getPage(page-1).rotateClockwise(angle))


                ###### filename formatting ######
                outfilename=outfileformat
                replacementlist=[("%0p","%0" + str(log10pages) + "p") , ("%n",name) , ("%e",ext)]
                applyreplacement=(lambda str, pair: str.replace(pair[0],pair[1]))
                applyreplacementlist=(lambda str, list=replacementlist, func=applyreplacement: reduce(func, [str]+list))

                outfilename=applyreplacementlist(outfilename, replacementlist)
                
                namearg = re.search('%[0-9]+n',outfilename)
                if namearg:
                    namearg=namearg.group()
                    filenum=int(namearg.strip("%n"))
                    (name, dot, ext) = inpdfargs[filenum-1][0].stream.name.rpartition(".")
                    outfilename = outfilename.replace(namearg, name)

                extarg = re.search('%[0-9]+e',outfilename)
                if extarg:
                    extarg= extarg.group()
                    filenum=int(extarg.strip("%e"))
                    (name, dot, ext) = inpdfargs[filenum-1][0].stream.name.rpartition(".")
                    outfilename = outfilename.replace(extarg, ext)

                if re.search('%[0-9]*i',outfilename):
                    outfilename = outfilename % (j+1)

                pmatch = re.search('%[0-9]*p',outfilename);
                if pmatch:
                    outfilename = re.sub('%[0-9]*p', (lambda smatch: smatch.group().replace("p", "i")), outfilename) % page

                while os.path.exists(outfilename):
                    if verbose: print ('error: '+outfilename+' already exists... appending number')
                    (oname, odot, oext) = outfilename.rpartition(".")
                    outfilename=oname+"-1"+odot+oext
                ###### end filename formatting ######

                outputStream = openpdf(outfilename, "out")
                if verbose: print "--write p" + str(page) + ">>" + outputStream.name
                output.write(outputStream)
                outputStream.close()
            else:
                sys.stderr.write( "Page" + str(page) + " is not found in file" + pdf.stream.name )
                sys.exit(3) #wrong pages or ranges            
            j=j+1
        i=i+1
    if verbose: print (str(j)+" pages in "+str(i)+" files processed")
###### end function burst ######

###### collate accepts a list of (PdfFileReader, [string pageselect]), string outfileformat
###### returns nothing, collates selected pages and writers to PdfFileWriter
def collate(inpdfargs, outfileformat):
    global verbose
    global ownerpassword
    global userpassword

    output = PdfFileWriter()
    if userpassword or ownerpassword:
        output.encrypt(userpassword,ownerpassword)
    if outfileformat == '-':
        verbose = False

    pagequeues = []
    maxpagecount=0
    for pdf, args in inpdfargs:
        numpages=pdf.getNumPages()
        if numpages > maxpagecount: maxpagecount=numpages
        replacements=[["end",str(numpages)]]
        pagequeues += [getpagequeue( args, replacements)]


    for pagei in range(maxpagecount):
        for pdfarg in inpdfargs:
            pdf, args = pdfarg
            pdfi = inpdfargs.index(pdfarg)
            numpages=pdf.getNumPages()
            try:
                page, angle = pagequeues[pdfi][pagei]
            except:
                page = -1
            else:
                if ( (page <= numpages) and (page > 0)):
                    if verbose: print "---add " + pdf.stream.name + ":p" + str(page)
                    output.addPage(pdf.getPage(page-1).rotateClockwise(angle))
    
    ###### filename formatting ######
    outfilename=outfileformat

    replacementlist=[("%n","%1n") , ("%e","%1e")]
    applyreplacement=(lambda str, pair: str.replace(pair[0],pair[1]))
    applyreplacementlist=(lambda str, list=replacementlist, func=applyreplacement: reduce(func, [str]+list))

    outfilename=applyreplacementlist(outfilename, replacementlist)

    namearg = re.search('%[0-9]+n',outfilename)
    if namearg:
        namearg=namearg.group()
        filenum=int(namearg.strip("%n"))
        (name, dot, ext) = inpdfargs[filenum-1][0].stream.name.rpartition(".")
        outfilename = outfilename.replace(namearg, name)
    
    extarg = re.search('%[0-9]+e',outfilename)
    if extarg:
        extarg= extarg.group()
        filenum=int(extarg.strip("%e"))
        (name, dot, ext) = inpdfargs[filenum-1][0].stream.name.rpartition(".")
        outfilename = outfilename.replace(extarg, ext)
    
    while os.path.exists(outfilename):
        if verbose: print ('error: '+outfilename+' already exists... appending number')
        (oname, odot, oext) = outfilename.rpartition(".")
        outfilename=oname+"-1"+odot+oext
    ###### end filename formatting ######

    outputStream = openpdf(outfilename, "out")
    if verbose: print "**Writing to " + outputStream.name
    output.write(outputStream)
    outputStream.close()
###### end function collate ######

###### concatenate accepts a list of (PdfFileReader, [string pageselect]), string outfileformat, bool inverse
###### returns nothing, joins selected (unselected if inverse is true) pages from PdfFileReaders and writers to PdfFileWriter
def concatenate(inpdfargs, outfileformat, inverse=False):
    global verbose
    global ownerpassword
    global userpassword

    output = PdfFileWriter()
    if userpassword or ownerpassword:
        output.encrypt(userpassword,ownerpassword)
    if outfileformat == '-':
        verbose = False

    for pdf, args in inpdfargs:
        numpages=pdf.getNumPages()
        replacements=[["end",str(numpages)]]
        pagequeue = getpagequeue( args, replacements)

        feedback = "**Processing: " + pdf.stream.name + " : "

        if inverse == False:
            if verbose:    print (feedback + "Sel" + str(pagequeue))
            for pageitem in pagequeue:
                page, angle = pageitem
                if ( (page <= numpages) and (page > 0)):
                    if verbose: print "---add p" + str(page)
                    output.addPage(pdf.getPage(page-1).rotateClockwise(angle))
                else:
                    sys.stderr.write( "Page" + str(page) + " is not found in file" + pdf.stream.name )
                    sys.qexit(3) #wrong pages or ranges
        else:
            pagelist = []
            for pageitem in pagequeue:
                pagelist += [pageitem[0]]
            if verbose:    print (feedback + "Rem" + str(pagelist[len(inputs)-1]))
            for page in range(1,numpages+1):
                if (page not in pagelist):
                    if verbose: print "--add p" + str(page)
                    output.addPage(pdf[-1].getPage(page-1))


    ###### filename formatting ######
    outfilename=outfileformat

    replacementlist=[("%n","%1n") , ("%e","%1e")]
    applyreplacement=(lambda str, pair: str.replace(pair[0],pair[1]))
    applyreplacementlist=(lambda str, list=replacementlist, func=applyreplacement: reduce(func, [str]+list))

    outfilename=applyreplacementlist(outfilename, replacementlist)

    namearg = re.search('%[0-9]*n',outfilename)
    if namearg:
        namearg=namearg.group()
        filenum=int(namearg.strip("%n"))
        (name, dot, ext) = inpdfargs[filenum-1][0].stream.name.rpartition(".")
        outfilename = outfilename.replace(namearg, name)
    
    extarg = re.search('%[0-9]*e',outfilename)
    if extarg:
        extarg= extarg.group()
        filenum=int(extarg.strip("%e"))
        (name, dot, ext) = inpdfargs[filenum-1][0].stream.name.rpartition(".")
        outfilename = outfilename.replace(extarg, ext)
    
    while os.path.exists(outfilename):
        if verbose: print ('error: ' + outfilename + ' already exists... appending number')
        (oname, odot, oext) = outfilename.rpartition(".")
        outfilename=oname+"-1"+odot+oext
    ###### end filename formatting ######

    outputStream = openpdf(outfilename, "out")
    if verbose: print "**Writing to " + outputStream.name
    output.write(outputStream)
    outputStream.close()
###### end function concatenate ######

def halp():
    print ("""\nUsage: pydftk MODE [-u=userpw] [-o=ownerpw] ARGUMENTS [OUTPUT]
  modes, and required arguments:
    sel,cat     inputfile [pagerange] [if2 [pr2]].. outputname
    del         inputfile [pagerange] [if2 [pr2]].. outputname
    col,zip     inputfile [pagerange] [if2 [pr2]].. outputname
    split,burst inputfile [pagerange] [if2 [pr2]]..[outputname]
    -h,--help   this help
    -v          verbose
    -q          quiet, disable verbose (forced when using <stdout>)
    **note:     - is replaced by <stdin> or <stdout> (determined by context)
                <stdout> is disabled for split/burst
                outputname can use formatting (see below)

  encrypt/decrypt:
    follow filename with -p=(pw) to decrypt using (pw)
    -u=(password) in arguments will set user password to (pw) for output
    -o=(password) in arguments will set owner password to (pw) for output

  pagerange formatting:
    range[SELECTION][:ROTATION]
    selection   can be e for even, o for odd, x# for every #th page
    rotation    can be r for right, l for left, u for up, d for down (180 deg)
                can also be cw# for clockwise, ccw# for counterclockwise
                cw and ccw # must be a multiple of 90 degrees
  pagerange examples:
    3           process page 3
    1-5         process pages 1,2,3,4,5
    5-1         process pages 5,4,3,2,1
    end-1       process all pages in reverse order (end replaced by last page)
    1-5o:cw90   process odd pages 1,3,5 and rotates each 90 degrees right
    1-7x3:d     process every 3rd page 1,4,7 and rotates each 180 degrees

  output formatting:
    sel/cat/del/col/zip:
      %n        %n or %1n is first file's path/name, %2n is second...
      %e        %e or %1e is first file's extension, %2e is second...
      -         used alone, will write output to <stdout>
    split/burst only:
      %n        is replaced by current file's path/name
      %e        is replaced by current file's extention
      %p        is replaced by page number, can be printf formatted
                %0p auto selects # of digits based on # pages in current file
      %i        is replaced by index number, can be printf formatted
  output examples:
    sel/cat/del/col/zip:
      $pydftk cat f1.e1 f2.e2 f3.e3 %3n-o.%e
      --would return a file named f3-o.e1
      $pydftk cat input.pdf -
      --would write all of input.pdf to <stdout>
    split/burst only:
      $pydftk burst input.pdf 5 %n.p%04p.%e
      --would return a file named input.p0005.pdf
      $pydftk burst input.pdf 5-6 %n.%03i.%e
      --would return input.001.pdf for page 5, input.002.pdf for page 6""")

###### end function halp ######


parse_args(sys.argv)