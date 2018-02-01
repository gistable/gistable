import os

paths = (os.path.join(root, filename)
        for root, _, filenames in os.walk('C:\FolderName')
        for filename in filenames)

for path in paths:
    # the '#' in the example below will be replaced by the '-' in the filenames in the directory
    newname = path.replace('#', '-')
    if newname != path:
        os.rename(path, newname)