#!/usr/bin/env python

import zipfile
import string
from lxml import etree

def read_docx(filepath):
    # todo: Add test to make sure it's a docx
    zfile = zipfile.ZipFile(filepath)
    # return the xml
    return zfile.read("word/document.xml")

def replace_hash(kp, input_string):
    for key, value in kp.items():
        if key in input_string:
            return value

def replace_docx(filepath, newfilepath, newfile):
    zin = zipfile.ZipFile(filepath, 'r')
    zout = zipfile.ZipFile(newfilepath, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename != 'word/document.xml'):
            zout.writestr(item, buffer)
        else:
            zout.writestr('word/document.xml', newfile)
    zin.close()
    zout.close()
    return True

def check_element_is(element, type_char):
     word_schema = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
     return element.tag == '{%s}%s' % (word_schema,type_char)

def docxmerge(fname, kp, newfname):

    filexml = read_docx(fname)
    my_etree = etree.fromstring(filexml)
    for node in my_etree.iter(tag=etree.Element):

        if check_element_is(node, 'fldChar'): #Once we've hit this, we're money...

            # Now, we're looking for this attribute: w:fldCharType="separate"
            if node.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldCharType') == "separate":
                node_value = node.getparent().getnext().getchildren()[1].text
                node.getparent().getnext().getchildren()[1].text = replace_hash(kp, node_value)

        elif check_element_is(node, 'fldSimple'): #Once we've hit this, we're money...
            node_value = node.getchildren()[0].getchildren()[1].text
            node.getchildren()[0].getchildren()[1].text = replace_hash(kp, node_value)

    replace_docx(fname, newfname, etree.tostring(my_etree, encoding='utf8', method='xml'))

if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description='Inject json into a mailmerged Word Document.')
    parser.add_argument('-f', '--file', help='the template file')
    parser.add_argument('-d', '--data', help='the data string')
    parser.add_argument('-o', '--output', help='the destination file')
    args = parser.parse_args()
    docxmerge(args.f, json.loads(args.d), args.o)
    print args.f + " merged."