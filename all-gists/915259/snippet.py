# Usage: python tt2srt.py source.xml output.srt

from xml.dom.minidom import parse
import sys
i=1
dom = parse(sys.argv[1])
out = open(sys.argv[2], 'w')
body = dom.getElementsByTagName("body")[0]
paras = body.getElementsByTagName("p")
for para in paras:
    out.write(str(i) + "\n")
    out.write(para.attributes['begin'].value.replace('.',',') + ' --> ' + para.attributes['end'].value.replace('.',',') + "\n")
    for child in para.childNodes:
        if child.nodeName == 'br':
            out.write("\n")
        elif child.nodeName == '#text':
            out.write(unicode(child.data).encode('utf=8'))
    out.write("\n\n")
    i += 1