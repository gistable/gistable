import os

def find(pathanme):
    for root, dirnames, filenames in os.walk(pathname):
        for f in filenames:
            yield os.path.join(root, f)

for f in find('/tmp'):
    print f