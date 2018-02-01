#!/usr/bin/python3
#######################################################
# Python rsync Backup script
# Sebastian Kraft, 24.06.2013
#
#######################################################

#-----------------------------------------------------
# Config

# Source directories
DIRECTORY_LIST = (
    "/home/kraft/Bilder",
    "/home/kraft/Dokumente",
    "/home/kraft/Projekte/",
    "/home/kraft/Videos/",
    "/home/kraft/Musik/"
)

# Target directory to store the backups
TARGET_DIRECTORY = "/media/kraft/fantec_ext4/Kraft_Backup/"

# Some settings
WRITE_LOGFILE         = True         # write a logfile to TARGET_DIRECTORY 

# TODO
#ALLOW_EMPTY_BACKUPS   = TRUE        # perform backup even if there are no changes detected by rsync
#CHECK_BACKUPS         = True        # check file consistency after every backup run 
#------------------------------------------------------

#######################################################

#------------------------------------------------------
# Some functions


def ask_ok(prompt, retries=4, complaint='Please type yes or no...'):
    while True:
        ok = input(prompt)
        if ok in ('y', 'Y', 'yes', 'Yes'):
            return True
        if ok in ('n', 'N', 'no', 'No'):
            return False
        print(complaint)


def print2log(s, filehandle=0):
    global WRITE_LOGFILE
    sys.stdout.buffer.write(bytes(s, "utf-8"))
    sys.stdout.flush()  
    # '\r' has no effect for file write
    if (WRITE_LOGFILE==True) and filehandle and (s.find('\r')==-1):
        filehandle.write(bytes(s, "utf-8"))

#------------------------------------------------------
# Main program

import time
import subprocess
import os
import sys
import re

# check if target directory is mounted
if not os.path.exists(TARGET_DIRECTORY):
    print("\nERROR: Target directory \n>> "+TARGET_DIRECTORY+" <<\nis not available! If it's located on an external or network drive check if it is correctly mounted in the expected place.\n\n")
    sys.exit()

# prepare logfile
if WRITE_LOGFILE:
    logFile = open(os.path.join(TARGET_DIRECTORY, 'rsync_' + time.strftime( "%Y-%m-%dT%H:%M:%S") + '.log'), 'wb')
else:
    logFile = 0

numBackupItems = len(DIRECTORY_LIST)
currBackupItem = 0

# iterate over directories
for backupDir in DIRECTORY_LIST:
    
    currBackupItem = currBackupItem + 1
    
    countStr = "("+str(currBackupItem)+"/"+str(numBackupItems)+")"
    
    print2log("\n-----------------------------------------------------------\n", logFile)
    print2log("Backing up " + backupDir + " " + countStr +"\n", logFile)
    print2log("-----------------------------------------------------------\n", logFile)
    
    # check if source directory exists    
    if not os.path.exists(backupDir):
        print2log("ERROR: Source directory does not exist! Skipping...\n", logFile)
        input("Press any key to proceed with next backup item...")
        continue

    timestamp = time.strftime( "%Y-%m-%dT%H:%M:%S")
    current_backup_target = os.path.join(TARGET_DIRECTORY, os.path.basename(os.path.normpath(backupDir)))
    previous_backup_link = ""

    # check for previous backups
    prevBackupsFound = False
    if os.path.exists(current_backup_target):
        dirListing = os.listdir(current_backup_target) 
        dirListing = [name for name in os.listdir(current_backup_target) if os.path.isdir(os.path.join(current_backup_target,name))]
        # match directory names of type 2013-06-24T18:44:31
        rex = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]{8}$')
        dirListing = [x for x in dirListing if rex.match(x)]
        numOldBackups = len(dirListing)
        if numOldBackups>0:
            #dirListing.sort(key=lambda s: os.path.getmtime(os.path.join(current_backup_target, s)))
            dirListing.sort()
            dirListing.reverse()
            previous_backup_link = os.path.join(current_backup_target, dirListing[0])
            print2log("Previous backup will be used as hard link reference: "+previous_backup_link+"\n", logFile)
            previous_backup_link = '--link-dest="' + previous_backup_link +'" '
            prevBackupsFound = True
    
    # if no old backups are found, ask to create a new one
    if not prevBackupsFound:
        print2log("WARNING: No previous data for incremental backups were found!\n", logFile)
        if ask_ok("Should a complete backup be performed? (y/n)"):
            if not os.path.exists(current_backup_target):
                os.mkdir(current_backup_target)
        else:
            # continue with next backup item
            continue            
            
    # assemble rsync commandline and run it
    rsynccmd  = 'rsync -aP ' + previous_backup_link + ' ' + backupDir + ' ' + os.path.join(current_backup_target,timestamp+"_tmp")
    print2log("+" + countStr + "+ " + rsynccmd + "\n\n", logFile)
    rsyncproc = subprocess.Popen(rsynccmd,
                                       shell=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
    )

    # read rsync output and print to console
    while True:
        next_line = rsyncproc.stdout.readline().decode("utf-8")
        if not next_line:
            break
        print2log("+" + countStr + "+ " + next_line, logFile)

    # wait until process is really terminated
    exitcode = rsyncproc.wait()
    # check exit code
    if exitcode==0:
        os.rename(os.path.join(current_backup_target,timestamp+"_tmp"), os.path.join(current_backup_target,timestamp))
        print2log("done \n\n", logFile)
    else:
        print2log("\nWARNING: looks like some error occured :( \n\n", logFile)
        break

# close logfile    
if (WRITE_LOGFILE==True) and logFile:
    logFile.close()