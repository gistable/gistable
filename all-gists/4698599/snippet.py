import urllib

class AdflySkipper:
    
    def __init__(self, url):
        self.url = url
    
    def extract(self):
        source = urllib.urlopen(self.url).readlines()
        for line in source:
            if "var zzz" in line:
                print line.split()[3].replace("'", '').replace(";", '')
                break
        
if __name__ == "__main__":
    url = raw_input("Adfly URL: ")
    if "adf" not in url:
        print "Invalid URL"
    else:
        AdflySkipper(url).extract()