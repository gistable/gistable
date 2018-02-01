import cssutils
from xml.sax import saxutils
from lxml.html import tostring, fromstring, clean
from lxml import etree

import logging

class Cleaner(clean.Cleaner):
    def clean_html(self, html):
        if not isinstance(html, unicode):
            raise ValueError('We only support cleaning unicode HTML fragments')

        #We wrap the content up in an extra div tag (otherwise lxml does wierd things to it - like adding in <p> tags and stuff)
        divnode = fromstring(u'<div>' + html + u'</div>')
        self(divnode)

        # Strip all class attributes
        etree.strip_attributes(divnode, 'class')

        for style in divnode.xpath("//@style"):
            parent = style.getparent()
            try:
                cssStyle = cssutils.parseStyle(style)
            except Exception, e:
                logging.info("Style %s failed to parse with error %s." % (style, e))
                parent.attrib.pop('style', None)
                continue

            # Set the line separator so that the style gets serialized
            cssutils.ser.prefs.lineSeparator = ''
            # Only allow valid style properties
            cssutils.ser.prefs.validOnly = True

            new_style = cssStyle.cssText
            if not new_style.strip():
                parent.attrib.pop('style', None)
            else:
                parent.attrib['style'] = new_style

        # Drop all empty span tags
        for span_tag in divnode.xpath("//span"):
            if not span_tag.keys():
                span_tag.drop_tag()

        #Now unwrap the divnode (i.e. just serialize the children of our extra div node)
        cleaned = saxutils.escape(divnode.text) if divnode.text else ''

        for n in divnode:
            cleaned += tostring(n, encoding = unicode, method = 'xml')
        return cleaned

# We need safe_attrs_only set to False, otherwise it strips out style attributes completely
cleaner = Cleaner(safe_attrs_only=False)
clean_html = cleaner.clean_html
