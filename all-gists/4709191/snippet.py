import os
import xml.etree.ElementTree as ET

DEBUG = 0

strXML = """<?xml version='1.0'?>
            <dir>
                <dir name="images">
                    <dir name="nuke" />
                    <dir name="maya" />
                </dir>      
                <dir name="cache">
                    <dir name="sim">
                        <dir name="ice" />
                        <dir name="nucleus" />
                    </dir>
                </dir>
            </dir>"""

element = ET.fromstring(strXML) # Replace with ET.parse() if reading a file
tree = ET.ElementTree(element)

root = tree.getroot()

def createDir(elem, basedir = None):
    """Creates directory structure from XML."""
        
    lDirs = elem.findall("dir")
    for i, each in enumerate(lDirs):
        
        oNewDir = os.path.join(basedir, each.get('name'))
        
        if DEBUG:
            log(oNewDir)
        
        if not os.path.isdir(oNewDir):
            os.mkdir(oNewDir)
        else:
            print oNewDir + " already exists"
            
        createDir(each, basedir = oNewDir)
    
    return
    
createDir(root, basedir = "C:\\Users\\Eric\\Desktop\\Temp\\DirBuild\\")