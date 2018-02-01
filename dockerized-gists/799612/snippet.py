#!/usr/bin/python
# Created by Christian Blades <christian dot blades at docblades dot com>

from xml.etree.cElementTree import Element, ElementTree
from urllib import quote_plus as quote

def _getData(line):
    name, text = None, None
    
    div = line.find(':')
    if div == -1:
        name = quote(line.strip())
    else:
        name = quote(line[:div].strip())
        text = line[div + 1:].strip()

    return name, text

def parse(theFile):
    elStack = []
    root = []
        
    for line in theFile:

        start = line.find("+ ")
        if (start == -1):
            continue
        else:
            name, text = _getData(line[start + 2:])
            
            myEl = Element(name)
            myEl.text = text
            
            if start == 0:                
                elStack = [[0, myEl]]
                root.append(myEl)
            else:                
                if start > elStack[-1][0]:
                    elStack[-1][1].append(myEl)
                    elStack.append([start, myEl])
                else:
                    while(elStack[-1][0] > start):
                        elStack.pop()
                        
                    elStack.pop()
                    elStack[-1][1].append(myEl)
                    elStack.append([start, myEl])

    rootNode = Element("root")

    for el in root:
        rootNode.append(el)
        
    return ElementTree(rootNode)

