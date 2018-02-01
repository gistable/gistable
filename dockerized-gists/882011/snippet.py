import time
import os
import logging
import sys
from subprocess import call, PIPE
import time, os, logging

MODEL_CLASSES = ['list','of','models','to','backup']

email = 'admin@email.com'

application = 'your-app-name'

app_dir = 'src/' #path to your application src (contains app.yaml. relative to this script)

local_url = 'http://localhost:8080/_ah/remote_api' # you need to have you local dev_appserver running, and it need the remote_api builtin turned on

# make a folder called backups.
def DownloadRemoteData(prefix='backups/', suffix='sql3'):
    global pass_file

    for model in MODEL_CLASSES:
    	print('**** Downloading: %s ****'%model)
        pass_file.seek(0)
        args = ['appcfg.py', 'download_data', '--passin', '--email=%s'%email, '--application=%s'%application, '--kind=%s'%model, '--filename=%s%s_backup.%s'%(prefix, model, suffix), app_dir]
            
        retcode = call(args, stdin=pass_file)
            
        time.sleep(1)
        
def RestoreLocalData(prefix='backups/', suffix='sql3'):
    global pass_file
        
    for model in MODEL_CLASSES:
    	print('**** Restoring: %s ****'%model)
        pass_file.seek(0)
        args = ['appcfg.py', 'upload_data', '--passin', '--email=%s'%email, '--application=%s'%application, '--kind=%s'%model, '--url=%s'%local_url, '--filename=%s%s_backup.%s'%(prefix, model, suffix), app_dir]
        
        retcode = call(args, stdin=pass_file)
            
        time.sleep(1)

def GetPassword():
    import getpass
    
    global pass_file
    
    pass_file = os.tmpfile()
    pass_file.write(getpass.getpass('password for %s:'%email))
    
def main(argv):
    GetPassword()
    
    DownloadRemoteData()
    RestoreLocalData()

    global pass_file
    pass_file.close()

if __name__ == "__main__":
    main(sys.argv)
