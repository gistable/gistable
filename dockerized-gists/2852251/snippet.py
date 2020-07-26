#!/usr/bin/python

import datetime
import subprocess
import sys
import os

class Commit(object):    
    def __init__(self, repo):
        """Initialization
        """
        self.now = datetime.datetime.now()
        self.repo=repo
        print "Committing "+ self.repo + " started at " +  self.now.strftime("%Y-%m-%d %H:%M")
        self.commit_message = ""
        self.commit_command = ""
        self.commit_complete_message = ""
        
    def commit_repo(self):
        """Commit 
        """         
        print "Entering " + self.repo
        if subprocess.call(["git","add","."], cwd=self.repo) != 0:
            exit(-1)
        self.commit_message = self.now.strftime("%Y-%m-%d %H:%M")
        if subprocess.call([ "git","commit","-m",self.commit_message ], cwd=self.repo) != 0:
            exit(-1)
        self.commit_complete_message = "Your repo -> " + self.repo + " has been successfully committed at " +  self.now.strftime("%Y-%m-%d %H:%M")
        print self.commit_complete_message
        if subprocess.call([ "git","push","-u","origin","main" ], cwd=self.repo) != 0:
            exit(-1)
        print "Pushed"
        

if __name__ == '__main__':
    repo = sys.argv[1]
    c = Commit(repo)
    c.commit_repo()