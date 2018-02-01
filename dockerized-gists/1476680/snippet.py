# Small Python Script to scrape websites for 
# email addresses and phone numbers(not a very great RE)
# Author: Dhruv Baldawa (@dhruvbaldawa on twitter)
# Github: http://www.github.com/dhruvbaldawa

import urllib,re
f = urllib.urlopen("http://www.example.com")
s = f.read()
re.findall(r"\+\d{2}\s?0?\d{10}",s)
re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}",s)

# Output
# ['+02 2323123789', '+01 2334325323', '+00 2323123323']
# ['user@example.com']