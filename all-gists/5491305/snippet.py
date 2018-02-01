#! /usr/bin/env python
# Brain-dead simple utility to dump a list of annotations from a Sony Reader .db 
# Usage: $ python annot2html.py [int number of annot to fetch]

import sys
import sqlite3 as sql
import xml.etree.ElementTree as ET

# Mac-path!
file_db = sql.connect('/Volumes/READER/Sony_Reader/database/books.db')
cur = file_db.cursor()

query = r'SELECT books.title, books.author, annotation.marked_text, annotation.mark FROM annotation INNER JOIN books on annotation.content_id = books._id'

cur.execute(query)
rows = cur.fetchall()

#how many rows?
num = -int(sys.argv[1]) if len(sys.argv) > 1 else 0

html = ET.Element('html')
head = ET.SubElement(html, 'head')
body = ET.SubElement(html, 'body')

for row in rows[num:]:
	stuff = ET.Element('li')
	stuff.text = row[2]+" "
	aut = ET.SubElement(stuff, 'em')
	aut.text = "("+row[0]+")"
	stuff.set("href", str(row[3]))
	body.append(stuff)

doc = ET.ElementTree(html)

print ET.tostring(html)