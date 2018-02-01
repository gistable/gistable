import os
import docx
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

os.chdir('C:\\OJT_Kevin\\161027_docx_parsing')

def iter_block_items(parent):
    """
    Yield each paragraph and table child within *parent*, in document order.
    Each returned value is an instance of either Table or Paragraph. *parent*
    would most commonly be a reference to a main Document object, but
    also works for a _Cell object, which itself can contain paragraphs and tables.
    """
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)
            
doc = docx.Document('sample.docx')
for block in iter_block_items(doc):
    if "Paragraph" in str(type(block)):
        print (block.text)
    elif "Table" in str(type(block)):
        for row in block.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    print (paragraph.text)