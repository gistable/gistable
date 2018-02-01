#!/usr/bin/env python
import argparse
import os, sys


try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile

#  w:tbl
#  ============================
#  w:tr
#  ----------------------------
#  w:tr
#  ----------------------------
#  w:tr | w:tc | w:tc
#  ----------------------------
#  w:tc <w:p><w:p><w:t>...
#  ----------------------------

class ExtractDocx(object):

    docx_ns = dict(
        wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
        mc="http://schemas.openxmlformats.org/markup-compatibility/2006",
        o="urn:schemas-microsoft-com:office:office",
        r="http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        m="http://schemas.openxmlformats.org/officeDocument/2006/math",
        v="urn:schemas-microsoft-com:vml",
        wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
        wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        w10="urn:schemas-microsoft-com:office:word",
        w="http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        w14="http://schemas.microsoft.com/office/word/2010/wordml",
        w15="http://schemas.microsoft.com/office/word/2012/wordml",
        wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
        wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
        wne="http://schemas.microsoft.com/office/word/2006/wordml",
        wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
        a="http://schemas.openxmlformats.org/drawingml/2006/main",
        a14="http://schemas.microsoft.com/office/drawing/2010/main",
        pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
        )

    docx_tags = dict(
            table              ='w:tbl',
            table_row          ='w:tr',
            table_cell         ='w:tc',
            table_p            ='w:p',
            table_t            ='w:t',
            )

    def __init__(self, file_path):
        document = zipfile.ZipFile(file_path)
        xml_content = document.read('word/document.xml')
        document.close()
        self.root = XML(xml_content)


    def inc_prefix(self, item):
        prefix, suffix = self.docx_tags[item].split(':')
        return '{{{0}}}{1}'.format(self.docx_ns[prefix], suffix)


    def find_all(self, item, top=None):
        if top is None:
            top = self.root
        return [elem for elem in top.iter(self.inc_prefix(item))]

    def get_table_data(self, top):
        rows = top.findall(self.inc_prefix('table_row'))
        row_data = []
        for row in rows:
            cell_data = []
            for cell in row.iter(self.inc_prefix('table_cell')):
                texts = [elem.text.strip() for elem in 
                           cell.iter(self.inc_prefix('table_t')) if elem.text is not None]

                cell_text = ''.join(texts)
                cell_data.append(cell_text)

            row_data.append(cell_data)

        return row_data



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "A script to read MS docx data")
    parser.add_argument('docx_file', help = "The path to the docx file to read")
    p = parser.parse_args()
    ed = ExtractDocx(p.docx_file)
    tables = ed.find_all('table')
    table_data = ed.get_table_data(tables[2])
    #for row in table_data:
    #    print row

