import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from collections import OrderedDict
# Store the xml file in the variable 'response'
response = urllib.request.urlopen("http://api.indeed.com/ads/apisearch?publisher=4964554191771748&q=java&l=gilroy%2C+ca&sort=&radius=&st=&jt=&start=&limit=&fromage=&filter=&latlong=1&co=us&chnl=&userip=1.2.3.4&useragent=&v=2")
#

# Dictionary where the Key is the type of information and the Value is the index where that information exists in 'results'.  I omitted unnecessary information to make it easier to look at.
stripped_data = OrderedDict([("Job Title:", 0), ("Company:", 1), ("Location:", 5) , ("Date:", 7), ("Snippet:", 8), ("URL:", 9)])

# Used xml.etree.ElementTree to iterate through elements in the xml file
tree = ET.parse(response)
root = tree.getroot()
# This is where the results are stored in the xml tree.  root[9][0] is the first job posting in the search.
results = root[9]
# A loop that goes through the individual posts in results and prints out the information at the indexes specified in stripped_data dictionary.
for posts in results:
    for key, value in stripped_data.items():
        if key == "URL:":
            print(key, posts[value].text + "\n") # Adds a line to seperate individual posts so they are easier to look at.
        else:
          print(key, posts[value].text)