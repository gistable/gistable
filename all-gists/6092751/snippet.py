'''A module for converting xml into json.'''

import json

from lxml import etree

def xml_to_json(xml_input, json_output):
    '''Converts an xml file to json.'''
    dict_to_json(etree_to_dict(xml_to_etree(xml_input), True), json_output)

def xml_to_etree(xml_input):
    '''Converts xml to a lxml etree.'''
    f = open(xml_input, 'r')
    xml = f.read()
    f.close()
    return etree.HTML(xml)

def etree_to_dict(tree, only_child):
    '''Converts an lxml etree into a dictionary.'''
    mydict = dict([(item[0], item[1]) for item in tree.items()])
    children = tree.getchildren()
    if children:
        if len(children) > 1:
            mydict['children'] = [etree_to_dict(child, False) for child in children]
        else:
            child = children[0]
            mydict[child.tag] = etree_to_dict(child, True)
    if only_child:
        return mydict
    else:
        return {tree.tag: mydict}

def dict_to_json(dictionary, json_output):
    '''Coverts a dictionary into a json file.'''
    f = open(json_output, 'w')
    f.write(json.dumps(dictionary, sort_keys=True, indent=4))
    f.close()