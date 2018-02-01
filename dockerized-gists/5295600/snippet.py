import zipfile, urllib, csv, os, codecs

def get_items(url):
    filename, headers = urllib.urlretrieve(url)
    try:
        with zipfile.ZipFile(filename) as zf:
            csvfiles = [name for name in zf.namelist()
                        if name.endswith('.csv')]
            for item in csvfiles:
                with zf.open(item) as source:
                    reader = csv.DictReader(codecs.getreader('iso-8859-1')(source))
                    for line in reader:
                        yield line
    finally:
        os.unlink(filename)