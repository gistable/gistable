
# coding: utf-8

# In[39]:

import os
#import fileinput
import sys
files=os.listdir(".")
#print(files)

datatypes = ['void','boolean','char','unsigned char','byte','int','unsigned int','word','long',
             'unsigned long','short','float','double','String','int8_t','uint8_t','int16_t','uint16_t','int32_t','uint32_t']


def parseparameters(paramstr):
    funcparams = []
    somethingfound = True
    while somethingfound :
        for dtype in datatypes:
            gotcha = paramstr.find(dtype)
            somethingfound = False
            if gotcha > -1:
                funcparams.append(dtype)
                #print('found',dtype,'at',gotcha)
                paramstr = paramstr[gotcha+len(dtype):]
                somethingfound = True
                break
    return funcparams
     


def checkiffunction(lnum,ftype,substr):
    a=0
    returnstr = []
    for letter in substr[::1]:
        if letter==';':
            #print('its a declaration')
            return False
        if letter=='[':
            #print('its an array')
            return False
        if letter=='=':
            #print('its a variable')
            return False
        if letter==')':
            #print('its a typecast or print or parameter')
            return False
        if letter=='(':
            substr2 = substr[a:]
            b = substr2.find(')')
            print(lnum,': could be a',ftype,'function named',substr[:a].lstrip())
            substr3 = substr2[1:b]
            if len(substr3) > 0:
                print('with parameters',substr3)
                pp = parseparameters(substr3)
                #print(pp)
                returnstr = ftype+' '+substr[:a].lstrip()+'('
                for p in pp:
                    returnstr += p +',' 
                returnstr = returnstr[:-1] #get rid of trailing comma
                returnstr += ');'
            else:
                print('')
                returnstr = ftype+' '+substr[:a].lstrip()+'();'
            return returnstr
        a += 1
    return False

for p in sys.argv: print(p)
fdeclarations = []
usagemsg="Usage \"python merg [outputname][.cpp]\""
outputname='output.cpp'
if len(sys.argv) > 0:
    if len(sys.argv) > 1:
        print(usagemsg)
        #sys.exit()
    #if '.cpp' in str(sys.argv[1]) :
    print (len(sys.argv))
    if (len(sys.argv) > 1):
        s=str(sys.argv[1]).find('.cpp')
    else: s=-1
    if (s != -1):
        outputname = str(sys.argv[1])
    else:
        if (len(sys.argv)>1):
            if (sys.argv[1] != "-f"):
                outputname = str(sys.argv[1])+'.cpp'
        else:
            outputname = 'output.cpp'
print("*** JOINING .INO FILES ***")
with open("temp.tmp", 'w') as fout:
     for f in files:
        print(f)
        if '.ino' in f: 
            print("<- is an ino file")
            with open(f) as infile:
                for line in infile:
                    fout.write(line)
        else: print('')
        
with open("temp.tmp") as infile:
    fdeclarations = []
    print("*** SEARCHING FOR FUNCTIONS ***")
    linenum=1
    for line in infile: #iterate through lines in temp file
        for dtype in datatypes: #iterate through different datatype that are being searched
            gotcha = line.find(dtype)
            if gotcha > -1: #there is something there
                #print('found',dtype,'on line',linenum,'at',gotcha)
                #print(line)
                dumbocounter=gotcha
                dumbo = line[dumbocounter]
                #protection against casts
                while dumbo != ' ' and dumbo != '(':
                    if dumbo == ')':
                        break
                    dumbocounter +=1
                    dumbo = line[dumbocounter]
                    if dumbo == '\n':
                        break
                if dumbo == ')':
                    print "{0} is a cast".format(str(linenum))
                    break
                if line[gotcha-1]== '(':
                    print "{0} is a cast".format(str(linenum))
                    break
                #protection
                if line[gotcha-2]== 'p' and line[gotcha-1]== 'r':
                    print "{0} is print".format(str(linenum))
                    break
                rstr = checkiffunction(linenum,dtype,line[gotcha+len(dtype)+1:])
                if rstr :
                    fdeclarations.append(rstr)
        linenum += 1
    print("")
    print(fdeclarations)
    print("*** ADDING FUNCTION DECLARATIONS TO .CPP FILE HEAD ***")
    fout = open(outputname,"w")
    includes_end_at = 1
    linenum = 1
    infile.seek(0)
    for line in infile: #iterate through lines in file
        if '#include' in line:
            includes_end_at = linenum
        linenum += 1
    linenum = 1
    print("includes end at line:",includes_end_at)
    fout.write("/* This file was automatically parsed from an Arduino sourcefile  */\n")
    fout.write("/* by PokittoParser v0.1 Copyright 2016 Jonne Valola              */\n")
    fout.write("/* USE AT YOUR OWN RISK - NO GUARANTEES GIVEN OF 100% CORRECTNESS */\n")
    infile.seek(0)
    for line in infile: #iterate through lines in file
        if linenum == includes_end_at + 1:
            fout.write("#include \"Pokitto.h\"\n")
            fout.write("/* Auto-generated function declarations */\n")
            for fd in fdeclarations:
                fout.write(fd+'\n') #write the declarations
            fout.write(line) #remember to add original line
        else:
            fout.write(line)
        linenum += 1
    fout.close()
    infile.close()
    print("*** DONE ! ***")

