# A collection of Python functions to make my life outside the Unity Editor Easier
# Author: Arturo Nereu @ArturoNereu
# License: Do whatever you want with the code

def removeMetaFiles(dirName):
        for root, dirs, files in os.walk(dirName):
                for name in files:
                        if name.endswith(".meta"):
                                fileToDelete = os.path.join(root, name)
                                print("Removing " + fileToDelete) ##Can be safely commented
                                os.remove(fileToDelete)
