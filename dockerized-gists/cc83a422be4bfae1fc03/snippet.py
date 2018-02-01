#!/usr/bin/env python
#-*- coding: utf-8 -*-
 
import subprocess
import string
import os
 
 
def getChangeList():
    """Retrieve the active Git change-list
    """
    files = subprocess.Popen(['git','--no-pager', 'diff', '--name-only', 'HEAD...origin'], stdout=subprocess.PIPE)
    results = files.stdout.read().split()
    return results
 
def fetchHead():
    subprocess.call(['git','fetch'])
    
def fetchLogs():    
    subprocess.call(['git','--no-pager','log','--stat','--no-merges','origin...HEAD'])
    
def pull():
    subprocess.call(['git','pull'])
    
def godRoot():
    filePath = subprocess.Popen(['git','rev-parse', '--show-toplevel'], stdout=subprocess.PIPE)
    return filePath.stdout.read().rstrip()
    
def main():
    """Update composer if `composer.lock` exists in the active change-list 
    """
    fetchHead()
    fetchLogs()
    changeList = getChangeList()
    pull()
  
    if 'composer.lock' in changeList:
        os.chdir(godRoot())
        subprocess.call(['composer', 'install'])
 
    if 'package.json' in changeList:
        os.chdir(godRoot())
        subprocess.call(['npm', 'install'])
 
if __name__ == '__main__':
    main()