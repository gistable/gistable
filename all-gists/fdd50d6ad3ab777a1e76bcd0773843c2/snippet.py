#!/usr/bin/env python3
# Scrapes breeding combinations from Siralim Wiki and writes them to a csv file
import csv
import requests
import re
from bs4 import BeautifulSoup

with open('Breeding Combinations.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
    html = requests.get('http://siralim.gamewiki.tips/doku.php?id=breeding').text
    soup = BeautifulSoup(html, 'lxml')

    # Creature families
    families = soup.find_all('h3', class_=re.compile('sectionedit'))
    # Tables containing breeding combinations
    tables = soup.find_all('table', class_='inline')

    writer.writerow(["Family", "Offspring", "Parent", "Mate"])

    for family, table in zip(families, tables):
        offspring = None
        for r in table.find_all('tr')[1:]:
            cols = [family.text] + [c.text for c in r.find_all(['th', 'td'])]
            if not cols[1].strip():
                # fill in empty offspring column
                cols[1] = offspring
            else:
                offspring = cols[1]
            writer.writerow(cols)