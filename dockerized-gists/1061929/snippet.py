"""
Mindmeister to OPML

Convert the JSON file embedded in mindmeister's native format
to OPML 1.0 that can be opened by OmniOutliner. For use with 
python 2.6 and above. For usage, run python mm2oo.py --help

Copyright (c) 2011 Matt Bowen (https://github.com/mattbowen)

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
"""
from optparse import OptionParser
from xml.etree import ElementTree as ET
import json
import htmllib

def parse_children(json_node, xml_parent):
    """Recurse through child nodes of the JSON, converting them
    to outline elements in the XML"""
    this_node = ET.SubElement(xml_parent, 
                              "outline", 
                              text=prep_text(json_node['title']))
    for child in json_node['children']:
        parse_children(child, this_node)
    return this_node

def convert_json_to_opml(json_root):
    """Setup the basic structure of an OPML tree and then call
    then parse the children into that tree"""
    opml_root = ET.Element("opml")
    opml_root.attrib["version"] = "1.0"
    #create the head
    head = ET.SubElement(opml_root, "head")
    title = ET.SubElement(head, "title")
    title.text = prep_text(json_root["title"])
    opml_root.append(head)
    body = ET.Element("body")

    parse_children(json_root, body)
    opml_root.append(body)
    return opml_root
    
    
def prep_text(intext):
    intext = intext.replace("\\r", ' ') #get rid of the line returns
    #convert the entities back into characters
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(intext)
    return p.save_end()

if __name__=="__main__":
    usage = "usage: %prog [options] infilename"
    parser = OptionParser(usage)
    parser.add_option("-o", "--output", dest="outfilename",
                      help='The name of the output file. '
                      'Defaults to infilename.opml', 
                      metavar="FILE")
    
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("You must provide at least an infile name")
    else:
        infilename = args[0]

    if options.outfilename is not None:
        outfilename = options.outfilename
    else:
        outfilename = ''.join((infilename.split('.')[0],'.opml'))

    with open(infilename) as infile:
        mindmap = json.load(infile)
        opml_tree = ET.ElementTree(convert_json_to_opml(mindmap['root']))
        opml_tree.write(outfilename)
