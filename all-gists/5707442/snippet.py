import xml.etree.ElementTree as ET

CDATA_KEY = "__CDATA__" #cdata tag name for sustitution

def monkey_patch():
    """Monkey Patch ElementTree, to support CDATA"""
    _serialize_xml = ET._serialize_xml

    def _serialize_xml_cdata(write, elem, encoding, qnames, namespaces):
        tag = elem.tag
        text = elem.text
        if tag == CDATA_KEY:
            write('<![CDATA[')
            if text:
                write(ET._escape_cdata(text, encoding))
            for e in elem:
                # we use the standart handler, because is not legal to have nested CDATA
                _serialize_xml(write, e, encoding, qnames, None)
            write(']]>')
        else:
            _serialize_xml(write, elem, encoding, qnames, namespaces)

    ET._serialize_xml = _serialize_xml_cdata
    print "ElementTree was Monkey Patched to suport CDATA"

monkey_patch()

##How To use:

element = ET.Element(CDATA_KEY) #this creates a CDATA element


