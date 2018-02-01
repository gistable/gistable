from lxml import etree
from copy import deepcopy
from math import ceil
 
itemsPerPage = 10

for inFile in ["episodes.all.m4a.rss", "episodes.all.mp3.rss"]:

    xmlData = etree.parse(inFile)
    
    items = xmlData.findall("//item") 
    
    for item in items:
        item.getparent().remove(item)
    
    pages = int(ceil(len(items) / float(itemsPerPage)))
    
    firstPage = inFile.replace(".all.", ".page%04d." % (1,))
    lastPage = inFile.replace(".all.", ".page%04d." % pages)
    
    for i in range(1, pages+1):
        startIndex = (i-1) * itemsPerPage;
        pageData = deepcopy(xmlData)
        filename = inFile.replace(".all.", ".page%04d." % i)
    
        channel = pageData.findall("//channel")[0]
        firstLink = etree.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
        firstLink.set("rel", "first")
        firstLink.set("type", "application/rss+xml")
        firstLink.set("title", "First Page")
        firstLink.set("href", "http://fanboys.fm/"+firstPage)
        
        lastLink = etree.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
        lastLink.set("rel", "last")
        lastLink.set("type", "application/rss+xml")
        lastLink.set("title", "Last Page")
        lastLink.set("href", "http://fanboys.fm/"+lastPage)
        
        if (i>1):
            prevLink = etree.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
            prevLink.set("rel", "previous")
            prevLink.set("type", "application/rss+xml")
            prevLink.set("title", "Previous Page")
            prevLink.set("href", "http://fanboys.fm/"+inFile.replace(".all.", ".page%04d." % (i-1,)))
            
        if (i<pages):
            nextLink = etree.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
            nextLink.set("rel", "next")
            nextLink.set("type", "application/rss+xml")
            nextLink.set("title", "Next Page")
            nextLink.set("href", "http://fanboys.fm/"+inFile.replace(".all.", ".page%04d." % (i+1,)))
            
        itemsOnPage = min(itemsPerPage, len(items) - (i-1)*itemsPerPage)
        
        for copyItem in items[startIndex:startIndex+itemsOnPage]:
            channel.append(copyItem)    
        
        f = open(filename, 'w')
        f.write(etree.tostring(pageData))
        f.close()
    
    
