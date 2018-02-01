import os

def doesFileExists(filePathAndName):
    return os.path.exists(filePathAndName)
  
# Example
if doesFileExists('./test.json'):
  print ('Yaa it exists!')
else:
  print ('Nope! Not around')