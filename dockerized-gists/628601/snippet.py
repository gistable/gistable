import simplejson as json
from lxml import etree

def is_node_badger_array(node):
    if len(node) <= 1:
        return False

    for (a,b) in zip(node,node[1:]):
        if a.tag != b.tag:
            return False

    return True

def body_to_pod(xml):
    is_arr = is_node_badger_array(xml)

    if is_arr:
        return {xml[0].tag: map(body_to_pod,xml)}
    else:
        obj = dict()

        for (key,val) in xml.attrib.iteritems():
            obj['@' + key] = val

        for child in xml.iterchildren():
            is_simple = (len(child) == 0 and len(child.attrib) == 0)
            obj[child.tag] = child.text if is_simple else body_to_pod(child)

        return obj

def from_pod_body(data,parent):
    elements = list()

    if not isinstance(data,dict):
        raise Exception('%s is not a dictionary!' % (data))

    for (key,value) in data.iteritems():
        if isinstance(value,list):                
            for item in value:
                itemEl = etree.Element(key)
                itemEl.extend(from_pod_body(item,itemEl))
                elements.append(itemEl)
        elif isinstance(value,dict):       
            itemEl = etree.Element(key)                                         
            itemEl.extend(from_pod_body(value,itemEl))
            elements.append(itemEl)
        else:
            if len(key) > 0 and key[0] == '@':
                parent.attrib[key[1:]] = value
            else:
                itemEl = etree.Element(key)
                itemEl.text = value
                elements.append(itemEl)

    return elements


def from_pod(data):
    els = from_pod_body(data,None)
    
    if len(els) == 0:
        raise Exception('Badgerfish json should be object on top level.')

    return els[0]
                
def to_pod(xml):
    return {xml.tag: body_to_pod(xml)}

def to_json(xml,**kargs):
    return json.JSONEncoder(**kargs).encode(to_pod(xml))

def from_json(json_data):
    return from_pod(json.load(json_data))
