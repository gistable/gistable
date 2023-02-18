from fabric.api import *
import os,json
from os.path import expanduser

env.forward_agent = True
USER_DETAILS = os.path.join(expanduser('~'),'userdetails.json')

def commit(message):
    local('git add .')
    local('git commit -m "' + message + '"')

def localpush(message):
    with settings(warn_only=True):
        commit(message)
    local('git push -u origin main')

def deploy(proj_path):
    with open(USER_DETAILS) as USERDETAILS:
        userdetails = json.load(USERDETAILS)[0]
    env.host_string = userdetails['host']
    env.password = userdetails['password']
    complete_path = os.path.join('/home',userdetails['host'].split('@')[0],proj_path)
    with cd(complete_path):
        run("git pull")

def remotepush(message,proj_path):
    localpush(message)
    deploy(proj_path)
    print "Code Sync Complete."

