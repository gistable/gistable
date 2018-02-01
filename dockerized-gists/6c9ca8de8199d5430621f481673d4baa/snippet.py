'''
Created on May 8, 2010 by @anasimtiaz

Updated on May 28, 2016 by @danielwrobert

This is a "fork" of original script.

Original script URL: http://anasimtiaz.com/?p=51
'''

import Tkinter, tkFileDialog, sys, os;
from Tkinter import *;

procInfo={};
fileFlag = False;
dirFlag = False;

def getFileName(srcFileDisplay):
    fileName = tkFileDialog.askopenfilename();
    srcFileDisplay.delete(0, END);
    srcFileDisplay.insert(0, fileName);
    procInfo['filename']=fileName;
 #   fileFlag = True;

def getOutDir(outDirDisplay):
    outputDir = tkFileDialog.askdirectory();
    outDirDisplay.delete(0, END);
    outDirDisplay.insert(0, outputDir);
    procInfo['outputdir']=outputDir;
#    dirFlag = True;

def writeHeader(currentFile):
    header = '''
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.2/"
>
<channel>
<wp:wxr_version>1.2</wp:wxr_version>'''
    
    currentFile.write(header);

def writeFooter(currentFile):
    footer = '''
</channel>
</rss>'''
    
    currentFile.write(footer);

def sysExit():
    sys.exit(1);
    
def startProc(statusDisplay):
    
    dispIndex = 1;
    
    if 'filename' in procInfo and 'outputdir' in procInfo:
    
        filePath,fileName = os.path.split(procInfo['filename']);
        fileNameTxt = os.path.splitext(fileName)[0];
        fileNameExt = os.path.splitext(fileName)[1];
        outDir   = procInfo['outputdir'];
        
        statusDisplay.insert(str(dispIndex)+'.0', 'Reading file ' + fileName + '\n');
        dispIndex += 1;
        xmlFileObj = open(os.path.join(filePath,fileName), "r");
        xmlFile = xmlFileObj.read();
        totalCount = len(xmlFile);
        iteration = 0;
        currentCount = 0;
        maxInc = 2000000;
        EOF = False;
    
    else:

        if 'filename' not in procInfo:
            statusDisplay.insert(str(dispIndex)+'.0', 'Source file not selected\n');
            #statusDisplay.insert('1.0', 'ERROR: Source file not selected\n');
            dispIndex += 1;
        
        if 'outputdir' not in procInfo:
            statusDisplay.insert(str(dispIndex)+'.0', 'Output Directory not selected\n');
            #statusDisplay.insert('2.0', 'ERROR: Output Directory not selected\n');
            dispIndex += 1;
        
        EOF = True;
    
    while(EOF==False):
        currentFileName = fileNameTxt + "_" + str(iteration) + fileNameExt;
        currentFile = open(os.path.join(outDir,currentFileName), 'w');
        statusDisplay.insert(str(dispIndex)+'.0', 'Writing file ' + currentFileName + '\n');
        dispIndex += 1;
        if iteration != 0:
            writeHeader(currentFile);
            
        if (currentCount+maxInc) < totalCount:
            xFile_i = xmlFile[currentCount:currentCount+maxInc];
            incrFile = xFile_i.rfind('</item>') + len('</item>');
            currentFile.write(xFile_i[:incrFile]);
            currentCount += incrFile;
        
        else:
            xFile_i = xmlFile[currentCount:];
            currentFile.write(xFile_i);
            statusDisplay.insert(str(dispIndex)+'.0', 'Finished processing \n');
            dispIndex += 1;
            EOF = True;
            
        if EOF != True:
            writeFooter(currentFile);
            
        iteration += 1;
       
            
            
            
if __name__ == '__main__':
    
    root = Tk();
    root.title('WordPress XML Splitter');
    
    srcFileText = Label(root, text="Source: ").grid(row=0, column=0, sticky=W);
    outDirText  = Label(root, text="Output Dir: ").grid(row=1, column=0, sticky=W);
 
    srcFileDisplay = Entry();
    srcFileDisplay.grid(row=0, column=1, columnspan=11);
    
    outDirDisplay = Entry();
    outDirDisplay.grid(row=1, column=1, columnspan=11);
    
    getAndDispFileName = lambda x=srcFileDisplay : getFileName(x);
    getAndDispOutDir   = lambda x=outDirDisplay  : getOutDir(x);
    
    browseSrcFile = Button(root, text="Browse File", command=getAndDispFileName).grid(row=0, column=12, sticky=W+E);
    browseOutDir  = Button(root, text="Browse Dir.", command=getAndDispOutDir).grid(row=1, column=12, sticky=W+E);
       
    statusDisplay = Text(root, width = 50, height = 10);
    statusDisplay.grid(row=2, column=0, columnspan=13);
    
    startProcPass = lambda x=statusDisplay : startProc(x);
    
    startButton = Button(root, text="Start", command=startProcPass).grid(row=3, column=6, sticky=W+E);
    exitButton = Button(root, text="Exit", command=sysExit).grid(row=3, column=7, sticky=W+E);
    
    
    root.mainloop();