#!/usr/bin/python

"""
- Submit example data to REVIGO server (http://revigo.irb.hr/)
- Download and run R script for creating the treemap
- Download and run R script for creating the scatterplot

Creates files:
    treemap.R, treemap.Rout, revigo_treemap.pdf
    scatter.R, scatter.Rout, revigo_scatter.pdf
"""

import os
import urllib
import mechanize

url = "http://revigo.irb.hr/"

# RobustFactory because REVIGO forms not well-formatted
br = mechanize.Browser(factory=mechanize.RobustFactory())

# For actual data, use open('mydata.txt').read()
br.open(os.path.join(url, 'examples', 'example1.txt'))
txt = br.response().read()

# Encode and request
data = {'inputGoList': txt}
br.open(url, data=urllib.urlencode(data))

# Submit form
br.select_form(name="submitToRevigo")
response = br.submit()

# Exact string match on the url for getting the R treemap script
br.follow_link(url="toR_treemap.jsp?table=3")
with open('treemap.R', 'w') as f:
    f.write(br.response().read())
    
# go back and get R script for scatter
br.back()
br.follow_link(url="toR.jsp?table=3")
with open('scatter.R', 'w') as f:
    f.write(br.response().read())
    # Downloaded scatter script doesn't save PDF, so add this line
    f.write('ggsave("revigo_scatter.pdf")')

# Create PDFs
os.system('R CMD BATCH treemap.R')
os.system('R CMD BATCH scatter.R')