# you can use something like this if read_html fails to find a table
# if you have bs4 >= 4.2.1, you can skip the lxml stuff, the tables
# are scraped automatically. 4.2.0 won't work.

import pandas as pd
from lxml import html

url = "http://www.uesp.net/wiki/Skyrim:No_Stone_Unturned"
xpath = "//*[@id=\"mw-content-text\"]/table[3]"

tree = html.parse(url)
table = tree.xpath(xpath)[0]
raw_html = html.tostring(table)

dta = pd.read_html(raw_html, header=0)[0]
dta["completed"] = 0
del dta["Map"]

table.make_links_absolute()
dta["map_link"] = [i[1][0].get('href') for i in table[1:]]