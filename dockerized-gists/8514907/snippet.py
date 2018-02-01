"""
Reportlab sandbox.
"""
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, landscape

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

doc = SimpleDocTemplate("form_letter.pdf",pagesize=landscape(letter),
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

Story=[]
logo = "image.png"

# We really want to scale the image to fit in a box and keep proportions.
im = Image(logo, 3*inch, 3*inch)
Story.append(im)

#ptext = '<font size=12>Some text</font>' 
#Story.append(Paragraph(ptext, styles["Normal"]))

ptext = '''
<seq>. </seq>Some Text<br/>
<seq>. </seq>Some more test Text
'''
Story.append(Paragraph(ptext, styles["Bullet"]))

ptext='<bullet>&bull;</bullet>Some Text'
Story.append(Paragraph(ptext, styles["Bullet"]))

doc.build(Story)
