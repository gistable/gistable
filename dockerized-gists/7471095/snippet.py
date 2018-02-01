import csv
from bs4 import BeautifulSoup

# Read in wheat production -----
wheat = {}
reader = csv.reader(open('aw98.csv'), delimiter=",")
#file has four lines of headers
next(reader, None) 
next(reader, None) 
next(reader, None) 
next(reader, None)
for row in reader: 
    try:
    	#county number 888 and 999 is a combination
    	if int(row[3]) < 888:
        	full_fips = row[1] + row[3]
        	rate = row[7] 
        	wheat[full_fips] = rate
    except:
        pass

# Load the SVG map
svg = open('counties.svg', 'r').read()

# Load into Beautiful Soup
soup = BeautifulSoup(svg, selfClosingTags=['defs','sodipodi:namedview'])

# Find counties
paths = soup.findAll('path')

# Map colors
colors = ["#F2F2F2", "#FFF7EC", "#FEE8C8", "#FDD49E", "#FDBB84", "#FC8D59", "#EF6548", "#D7301F", "#B30000", "#7F0000" ]

# County style
path_style ='font-size:12px;fill-rule:nonzero;stroke:#FFFFFF;stroke-opacity:1;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;marker-start:none;stroke-linejoin:bevel;fill:'

# Color the counties based on wheat production
#the bin points are fairly arbitrary
for p in paths:
 
    if p['id'] not in ["State_Lines", "separator"]:
        # pass
        try:
            if p['id'] in wheat:
                rate = int(wheat[p['id']])
            else:
                rate = int(0)
        except:
            continue
        if rate == 0:
            color_class = 0
        elif rate < 40000:
            color_class = 1
        elif rate < 115500:
            color_class = 2
        elif rate < 270000:
            color_class = 3
        elif rate < 600000:
            color_class = 4
        elif rate < 1701000:
            color_class = 5
        elif rate < 6500000:
            color_class = 6
        elif rate < 1000000:
            color_class = 7
        elif rate < 1500000:
            color_class = 8        
        else:
            color_class = 9
 
        color = colors[color_class]
        p['style'] = path_style + color
        
# Output map
print soup.prettify()