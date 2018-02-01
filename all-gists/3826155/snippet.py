def recurse(element):
  elements = []
  for item in element.objectValues():
    d = {'uid' : item.UID(), 
         'title' : item.title,
         'children' : []}
    if hasattr(item, 'objectValues'):
      d['children'] = recurse(item)
    elements.append(d)
  return elements

def indent(text, level):
  return (' '.join([' ' for i in range(0, level * 2)])) + text + '\n'

def prettyPrint(elements, level):
  result = ""
  for element in elements:
    result += indent('<term>', level)
    result += indent('  <termIdentifier>%s</termIdentifier>' % element['uid'], level)
    result += indent('  <caption>', level)
    result += indent('    <langstring language="da">%s</langstring>' % element['title'], level)
    result += indent('  </caption>', level)
    result += prettyPrint(element['children'], level + 1)
    result += indent('</term>', level)
  return result

result = recurse(context)
print """
<?xml version="1.0" encoding="UTF-8"?>
<vdex xmlns="http://www.imsglobal.org/xsd/imsvdex_v1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsvdex_v1p0 imsvdex_v1p0.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd" orderSignificant="false" profileType="flatTokenTerms" language="en">

  <vocabName>
    <langstring language="da">EDIT TITLE</langstring>
  </vocabName>

  <vocabIdentifier>EDIT NAME</vocabIdentifier>
"""
print prettyPrint(result, 1)
print "</vdex>"
return printed
