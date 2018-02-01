import os, zipfile, string
from xml.dom.minidom import parse
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

folder = input("Folder: ")
for f in os.listdir(folder):
    if os.path.splitext(f)[1] == ".epub":
        z = zipfile.ZipFile(folder + f, 'r')
        for name in z.namelist():
            if ".opf" in name:
                dom = parse(z.open(name))
                title = dom.getElementsByTagName('dc:title')[0].firstChild.nodeValue
                z.close()
                newname = ''.join(c for c in title if c in valid_chars) + '.epub'
                print(newname)
                if newname not in os.listdir(folder):
                    os.rename(folder + f, folder + newname)