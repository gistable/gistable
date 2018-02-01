


import os
import sys
import time, json, datetime
import ntpath
import subprocess

maxFiles = 100000000
test = False
fileEndings = (".jpg", ".jpeg", ".png", ".mov", ".mp4", ".srw", ".m4v")

os.chdir(os.path.join(os.getcwd(), "Core Pictures"))

print( os.getcwd())

def setCreationTime( filePath, time ):
    print( "\t\tSetting Creation Time to: " + str(time))
    timeSetFile = time.strftime("%m/%d/%Y %H:%M:%S")
    #timeTouch = time.strftime("%Y%m%d%H%M")
    commandSetTime = ["SetFile", "-d", timeSetFile, filePath]
    #commandTouch = ["touch", "-t", timeTouch, filePath]
    #strCmd = "SetFile -t " + time + " '" + filePath + "'" 

    command = commandSetTime

    commandStr = ''
    for s in command:
        commandStr += s + ' '

    print("\t\tCOMMAND:    " + str(command))
    print("\t\tCOMMANDSTR: " + str(commandStr))
    #subprocess.call(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    print("\t\t" + subprocess.check_output(command))
    #rc = subprocess.Popen(strCmd, )

def getAllFiles( endswith=None ):
    fileNameList = {}
    n = 0

    for root, subfolders, files in os.walk(os.getcwd()):
        for file in files:
            filePath = os.path.join(root,file)
            modified = time.ctime(os.path.getmtime(filePath))
            modified = datetime.datetime.strptime(modified, "%a %b %d %H:%M:%S %Y")
            created = time.ctime(os.path.getctime(filePath))
            created = datetime.datetime.strptime(created, "%a %b %d %H:%M:%S %Y")

            if endswith != None and not filePath.lower().endswith(endswith):
                continue
            elif ntpath.basename(filePath).startswith("."):
                continue
            else:
                fileNameList[filePath] = {"modified": modified, "created": created}
            n+=1
            if n > maxFiles: break

        if n > maxFiles: break
    return fileNameList

files = getAllFiles(endswith=fileEndings )

print("Found: " + str(len(files)) + " files of types " + str(fileEndings))

i = 0
for f in files:
    print(str(f))
    print("\t\tCreated: " + str(files[f]['created']))
    print("\t\tModified: " + str(files[f]['modified']))

    if files[f]['modified'] < files[f]['created']:
        print("\t\tMODIFIED BEFORE CREATED")

    setCreationTime( f, files[f]['modified'])


    i+=1
    if i > maxFiles: break

exit()


for f in files:
    data = files[f]
    year = str(data['modified'].year)
    if data['modified'].month < 10:
        numMonth = "0" + str(data['modified'].month)
    else:
        numMonth = str(data['modified'].month)
    month = numMonth + " - " + str(data['modified'].strftime("%B"))

    print( f + " Modified: " + month + ", " + year)

    yearDir = os.path.join(os.getcwd(), year)
    monthDir = os.path.join(yearDir, month)

    # If it is already in the correct directory, then skip. Nothing to do
    if monthDir in f:
        print("\t\tCORRECT LOCATION")
        continue
    else:
        print("\t\tINCORRECT LOCATION")
        if not os.path.exists(monthDir):
            print("\t\tDirectory does not exist. Making: " + monthDir)
            if not test:
                os.makedirs(monthDir)

        fileName = ntpath.basename(f)
        correctLocation = os.path.join(monthDir, fileName)
        print( "\t\tMoving File:")
        print( "\t\t\tFrom: " + f)
        print( "\t\t\tTo:   " + correctLocation )
        if not test:
            os.rename(f, correctLocation)