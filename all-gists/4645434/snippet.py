import urllib, os, sys, zipfile

def download(url,name=""):
    if(name == ""):
        name = url.split('/')[-1]
    webFile = urllib.urlopen(url)
    localFile = open(name, 'w')
    fname = localFile.name
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()
    return fname
    
baseurls = {'parcels': r"http://njgin.state.nj.us/download2/parcels/parcels_mdb_{COUNTY}.zip", 'taxlist': "http://njgin.state.nj.us/download2/parcels/parcels_taxlistsearch_{COUNTY}.zip"}
counties = ["Atlantic", "Bergen", "Burlington", "Camden", "CapeMay", "Cumberland", "Gloucester", "Hudson", "Hunterdon", "Mercer", "Monmouth", "Morris", "Ocean", "Passaic", "Salem", "Somerset", "Sussex", "Union", "Warren"]
for dt in baseurls.keys():
    for county in counties:
        url = baseurls[dt].replace("{COUNTY}", county)
        fn = url.split('/')[-1]
        if(os.path.exists(fn)):
            print county, dt, "zip file already downloaded."
        else:
            fn = download(url)
            print county, "downloaded."

        zipf = zipfile.ZipFile(fn, "r")
        names = zipf.namelist()
        if(len(names)==1):
            if(not os.path.exists(dt+names[0])):
                outz = open(dt+names[0], "wb")
                outz.write(zipf.read(names[0]))
                outz.close()
                print county, dt, "extracted."
            else:
                print dt+names[0], "already exists. Skipped."
 
