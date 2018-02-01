import os
import time
import sys

# Function to execute shell commands "built ins"
# 
def executeBuiltin(cmd):
    if cmd[0] == "pwd":    # Rudimentary builtin check
        pwd()
    elif cmd[0] == "cd":
        if len(cmd) == 1:
            chdir(os.getenv('HOME'))
        else:
            chdir(cmd[1])
    elif cmd[0] == "exit":
        os._exit(0)
    else:
        pass

# Stuff with a "> , <" get sent here
# cmd is list, first is first file descriptor)
# 2nd is 2nd file descriptor
# Ex. cat file1 > file2
# ex. echo "test" > file2

def redirect(cmd):
    
    if cmd[2] == ">":
        fd1 = os.open(cmd[1], os.O_RDWR|os.O_CREAT)
        os.dup2(fd1,1)     #Duplicate fd's
        os.close(fd1)
        
    elif cmd[2] == "<":
        fd2 = os.open(cmd[3], os.O_RDWR|os.O_CREAT)
        os.dup2(fd2,1)    #duplicate STDOUT to FD
        os.close(fd2)
    else:
        print "Cannot open files for redirection!"

    

def pwd():
   print "Current directory: " +  os.getcwd()

def chdir(path):
    os.chdir(path)
    print "Path changed to: " + path

def startShell():
    # Calculate time
    localtime = time.asctime(time.localtime(time.time()) )

    #Builtin list
    builtins = ["cd", "pwd", "exit"]
    redir_ops = [">", "<"]
    
    while True:
        #Get Input
        line = raw_input(localtime + ' Shell> ').split()
        
        if line[0] in builtins:
            executeBuiltin(line)
        elif line[2] in redir_ops:
            redirect(line)
        else:
            # Not a builtin, fork
            newpid = os.fork()
            
            if newpid == -1:
                print "Fork Error!"
                os._exit(1)
            elif newpid == 0:
                # In child
                os.execvp(line[0], line)

            else:
                os.waitpid(newpid, 0)

startShell()

        
    
