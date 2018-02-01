import os,sys,importlib
from os import path
def RunScript(sPath,sFile,bDirect=2):
    ''' Run a Python Script via differenct Methods
    @param sPath Sting containing Only the
                 Absolute Path of the File to Execute
    @param sFile String containing Only the File Name to Execute
    @param bDirect Flag indicates how to run the Script
                    0 = Run using Exec Technique
                    1 = Run directly in Shell
                    2 = Import Module and call run() function
    @exception In case of any error both in the script or the execution, it
                 shall be reported
    @return None
    '''
    try:
        if bDirect == 0:
            sRunPath = sPath
            with open(path.join(sPath,sFile)) as f:
                exec(compile(f.read(), "temp.p", 'exec'), globals())
        elif bDirect == 1:
            tmp = os.getcwd()
            os.chdir(sPath)
            os.system("python " + sFile)
            os.chdir(tmp)
        elif bDirect == 2:
            sys.path.insert(0,sPath)
            tmp = importlib.import_module(sFile.split(".py")[0])
            tmp.run()
            sys.path.remove(sPath)
        else:
            pass
    except BaseException as p:
        print("\nProblem in Running",sFile,"at",sPath,"Script :",p)