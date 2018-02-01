import json
from bs4 import BeautifulSoup
import re

of = open("all_output.txt", "wb")

for file_num in range(1,102):
    filename = "%03d.json" % file_num
    print filename


    with open(filename) as data_file:    
        data = json.load(data_file)

    html = data['results_html']

    doc = BeautifulSoup(html, "lxml")

    rows = doc.find_all('div',class_="market_listing_row market_recent_listing_row")

    for item in rows:
        if item.find(text=re.compile("Buyer:")):
            name = item.find('span',class_="market_listing_item_name").text.strip()
            name = name.replace(',','_')
            date = item.find('div',class_="market_listing_right_cell market_listing_listed_date").text.strip()
            sold_price = item.find('span',class_="market_listing_price").text.strip()
            # print "%s,%s,%s" % (date,name,sold_price)

            of.write( ("%s,%s,%s\n" % (date,name,sold_price)).encode('utf-8')  )

of.close()
