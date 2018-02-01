########################################################################################
## ezTD_mobuSetup.py
## version: 2.0
## Author:  Jason Barnidge
##          jbarnidge [at] OmniZed.com
##          www.OmniZed.com
## Description: 
##      Easily setup & maintain a standardized pipeline for Animators in MotionBuilder
##      Also helpful when/if a MotionBuilder bug resets the config files
########################################################################################
 
from pyfbsdk import *
import os
import os.path
 
lApp = FBApplication()
lSystem = FBSystem()
 
lconfigHistory = FBConfigFile("@History.txt")
lconfigApp = FBConfigFile("@Application.txt")
 
##============\ START EDITING PATHS BELOW TO SUIT YOUR PIPELINE NEEDS /=============##
""" Set a value to None for it to remain unchanged. 
    For example:  newFavPaths = None """
 
## FAVORITE PATHS (list) - Added to the Asset Browser
newFavPaths = [ (r"D:\MyProject\Animations"),
                (r"D:\MyProject\Rigs"),
                (r"D:\MyProject\Poses")]
 
## PYTHON STARTUP DIRECTORY (str)
pyStartupDir = r"D:\MyProject\MotionBuilder\PythonStartup"
 
## ADDITIONAL PLUGINS DIRECTORIES (list) 
pluginDirs = [(r"D:\MyProject\MotionBuilder\plugins"),
                (r"D:\MyProject\MotionBulder\3rdParty\plugins")]
##==============/ STOP EDITING OF PATHS HERE FOR YOUR PIPELINE NEEDS \=============##
 
 
########################################################################################
def populateFavList(pList):
    for i in xrange(len(pList)+1):
        iFav = "Favorite%d" % (i + 1)
        lVal = lconfigHistory.Get("Templates", iFav)
        if (lVal != None) and lVal not in pList:
            lVal = r"%s" % lVal
            print lVal
            pList.append(lVal)
            populateFavList(pList)
        elif lVal in pList: continue
        elif lVal == None:
            return pList
 
########################################################################################
def EZTDsetup(newFavPaths = None, pyStartupDir = None, pluginDirs = None):
    """ parameters:
            newFavPaths[list] - list of directories
            pyStartupDir[string] - path of directory
            pluginDirs[list] - list of directories
        returns: False - if a directory does not exist
    """
    # Favorites in Asset Browser
    if newFavPaths != None:
        lFavList = []
        populateFavList(lFavList)
        lNumFavs = len(lFavList)
        for n in xrange(len(newFavPaths)):
            if os.path.exists(newFavPaths[n]) == False:
                print "%s << This directory does not exist." % newFavPaths[n]
                return False
            else:
                if newFavPaths[n] not in lFavList:
                    print "%s not found in favorites.\nPath is now being added.\n" % newFavPaths[n]
                    lNewFav = "Favorite%d" % (lNumFavs + n + 1)
                    lconfigHistory.Set("Templates", lNewFav, newFavPaths[n])
    else:
        print "Asset Browser's Favorites Folders remain unchanged. No new paths were specified."
    # Python
    if (pyStartupDir != None):
        if os.path.exists(pyStartupDir):
            lconfigApp.Set("Python", "PythonStartup", pyStartupDir, "IMPORTANT FOR CUSTOM STARTUP TOOLS")
        else:
            print "%s << This directory does not exist." % pyStartupDir
            return false
    else:
        print "PythonStartup directory remains unchanged. No new path was specified."
    # AdditionnalPluginPath    
    if pluginDirs != None:
        numPlugins = str(len(pluginDirs))
        lconfigApp.Set("AdditionnalPluginPath", "Count", numPlugins )
        for p in xrange(len(pluginDirs)):
            if os.path.exists(pluginDirs[p]) == False:
                print "%s << This directory does not exist." % pluginDirs[p]
                return False
            else:
                iPlugInVal = "PlugInPath%d" % p
                lconfigApp.Set("AdditionnalPluginPath", iPlugInVal, pluginDirs[p], "insert comment/info here if desired but not necessary")
    else:
        print "Plugin Paths remain unchanged. No paths were specified."
 
    return True
 
########################################################################################
 
setupComplete = EZTDsetup(newFavPaths, pyStartupDir, pluginDirs)
 
if setupComplete == True:
    lMsg = "Congratulations!\n"
    lMsg += "Your MotionBuilder Pipeline was Successfully Installed.\n\n"
    lMsg += "Please restart MotionBuilder for changes to take effect."
    FBMessageBox( "EZ TD Setup for MotionBuilder", lMsg, "OK", None, None )
else:
    lMsg = "ERROR: Tools & Pipeline Installation was Unsuccessful.\n\n"
    lMsg += "*Contact a Technical Artist / Animator for further assistance."
    FBMessageBox( "EZ TD Setup for MotionBuilder", lMsg, "OK", None, None )