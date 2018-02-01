import os
import fnmatch


def dirwalk(directory, pattern="*"):
    "walk a directory tree, using a generator"
    for name in os.listdir(directory):
        fullpath = os.path.join(directory, name)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for name in dirwalk(fullpath):  # recurse into subdir
                if fnmatch.fnmatch(name, pattern):
                    yield name
        elif fnmatch.fnmatch(fullpath, pattern):
            yield fullpath


if __name__ == "__main__":
    for file in dirwalk("c:\\tmp", "*.py"):
        print file
