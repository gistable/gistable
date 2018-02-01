import os


def removeEmptyFolders(path):
    if not os.path.isdir(path):
        return

    # walk through folders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath)

    # delete empty folders
    if len(files) == 0:
        print "Remove empty folder: ", path
        os.rmdir(path)

if __name__ == "__main__":
    removeEmptyFolders('/home/noxan/Music/')
