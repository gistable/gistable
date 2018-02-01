import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, element
import urllib2, re

# Read the HTML from the webpage on Wikipedia stats and convert to soup
soup = BeautifulSoup(urllib2.urlopen('http://stats.wikimedia.org/EN/TablesWikipediaEN.htm').read())

# Look for all the paragraphs with 2014
_p = soup.findAll('b',text=re.compile('2014'))

# Select only those paragraph parents that have exactly 152 fields, corresponding to the top-25 lists
_p2014 = [t.parent for t in _p if len(t.parent) == 152]

# Get the text out of the children tags as a list of lists
parsed = [[t.text for t in list(p.children) if type(t) != element.NavigableString] for p in _p2014]

# Convert to a dictionary keyed by month abbreviation with values as the list of text fields
parsed = {month[0].split(u'\xa0')[0]:month[1:] for month in parsed}

# Do some crazy dictionary and list comprehensions with zips to convert the values in the list
parsed = {k:[{'rank':int(a),'editors':int(b),'article':c} for a,b,c in zip(v[0::3],v[1::3],v[2::3])] for k,v in parsed.items()}

# Convert each month into a DataFrame with month information in the index
# and then concat all the dfs together, sorting on those with the most editors
ranked = pd.concat([pd.DataFrame(parsed[i],index=[i]*len(parsed[i])) for i in parsed.keys()]).sort('editors',ascending=False).reset_index()

# rename the reset index to something meaningful
ranked.rename(columns={'index':'month'},inplace=True)

# Group the articles by name, compute aggregate statistics
# Rank on the total number editors and months in the top 25
top_articles = ranked.groupby('article').agg({'month':len,'editors':np.sum,'rank':np.min}).sort(['month','editors'],ascending=False)
top_articles