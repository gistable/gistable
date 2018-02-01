#!/usr/bin/env python

""" Stack Overflow XML 2 SQL

The following is a custom made XML 2 SQL converter for Stack Overflow data.

Latest Stack Overflow Data: August 2012

Call Examples: 

  python so_xml2sql.py posts.xml comments.xml
  
  python so_xml2sql.py *.xml

WARNING: You must construct the database before you import the SQL file. For
most part the XML 2 SQL will be taking the XML structure for Stack Overflow
and creating INSERT statements. The following is example of the conversion.

entity.xml
----------
<Entity>
  <row attr1="value" attr2="value" ... />
  <row attr1="value" attr2="value" ... />
</Entity>

entity.sql
----------
INSERT INTO Entity (attr1, attr2, ... )
VALUES
("value", "value", ... ),
("value", "value", ... );

It's fairly straight forward. This is a conversion script so it will not
import the SQL file into your database so you can run the conversion, then
setup the database, and finally import the database. The script will try to
output helpful information into entity.info so that you could get some sense
about the data you will be importing but don't rely on it (You must specify the
--info flag though for this to occur).

WARNING: posthistory.xml has some XML 1.1 encodings and therefore need to be
taken out. The following command using sed can allow you to do this. I have
it create a new version (wastes space) but allows you to have both versions
so you can decide what to do:

sed 's/&#xB;//g;s/&#xC;//g;s/&#x1A;//g;s/&#x1B;//g' posthistory.xml > \
posthistory_fix.xml

(Hopefully the backslash will properly escape the new line character if not
just know that it is outputting the result to posthistory_fix.xml so
you should put it after the > but I do this to keep within 80 character limit
sorry for the inconvenience it may cause)
"""

import argparse
import re
import sys
import xml.etree.cElementTree as xml

def compile_insert(table, child):
  """ Compiles the SQL INSERT statement for the child.

  Since each child will not have same attributes, I'd rather just compile
  separate INSERT statements. This may be slower but less error prone unless
  you pass in all the attributes from the start so it knows which attributes
  to set as NULL if they don't exist. Returns the sql_statement. """
  sql_statement = ""
  cols = child.attrib.keys()

  sql_statement += "INSERT INTO %s (" % (table)
  for i in range(0, len(cols)):
    column = cols[i]
    if column == "CloseReasonId":  #CloseReasonId actually in Comment attr
      column = "Comment"
    sql_statement += "%s" % (column)
    if i != len(cols) - 1:  
      sql_statement += ", "
    else:
      sql_statement += ") "   # Last one outputs the end of the statement

  # Begin writing the actual valued elements
  sql_statement += "VALUES ("

  # Write each attribute to the file
  for i in range(0, len(cols)):
    sql_value = "%r" % (child.attrib[cols[i]])
    if sql_value[0] == 'u':   # Remove unicode marking for value
      sql_value = sql_value[1:]
    sql_statement += sql_value

    if i != len(cols) - 1:  # Last one outputs the end of the statement
      sql_statement += ", "
    else:
      sql_statement += ");\n"

  return sql_statement

def convert(filename, info):
  """ Convert an XML file to SQL.

  Takes in an XML file's name and an info flag of whether or not to output
  information data to a .info file. Converts the XML file to SQL and outputs
  a .sql file. Returns whether the conversion was successfully or not.
  """
  basename = filename[:-4]      # Base name is without the .xml
  sqlfile = basename + ".sql"   # SQL output file
  infofile = basename + ".info" # Info file for outputting stats

  # Touch the file - This may be more inefficient but rather append then write
  # all at once just in case of crash in between also can avoid possible
  # paging limits if any exist
  output = open(sqlfile, 'w')
  output.close()

  # Begin conversion
  tree = xml.iterparse(filename, events=("start", "end"))
  tree = iter(tree)
  event, entity = tree.next()

  tree = xml.iterparse(filename)  # Reset to just be the end tags for rows
  tree = iter(tree)

  children = 0
  attributes = None
  # Convert each child to INSERT Statement
  for event, child in tree:
    if child.tag == entity.tag: # We are at the end tag
      break
    if children == 0:
      attributes = child.attrib.keys()
    # Deal with compiling INSERT statement and outputting
    sql_statement = compile_insert(entity.tag, child)
    output = open(sqlfile, 'a')
    output.write(sql_statement)
    output.close()
    # Management
    children += 1
    entity.clear()
    child.clear()

  # Deal with Statistics
  if info:
    info_output = open(infofile, 'w')
    info_output.write("Entity Table: %s\n" % (entity.tag))
    info_output.write("Entity Entries: %d\n" % (children))
    info_output.write("First Entry's Columns\n")
    for col in attributes:
      info_output.write("  %s\n" % (col))
    info_output.close()

  return True

if __name__ == "__main__":
  # Setup the parsing of the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", nargs='+', 
                      help="name of file to be converted")
  parser.add_argument("-i", "--info", help="output information about data",
                      action="store_true")
  args = parser.parse_args()

  # Verify the file names are xml files
  for inputfile in args.filename:
    if not re.match("^.*\.xml$", inputfile):
      print "Error File: %s. You must enter XML files only." % (inputfile)
      sys.exit(1)

  # Start the conversion process
  print "Stack Overflow XML2SQL Converter\n"
  if args.info:
    print "Flags Set"
    print "[ON] Information output.\n"

  print "Beginning Converting Files"
  # Convert each file to SQL
  for inputfile in args.filename:
    print "[Converting] %s." % (inputfile)
    success = convert(inputfile, args.info)
    if success:
      print "             Successfully converted %s." % (inputfile)
    else:
      print "             Errors exist. See above for error messages."

  # Completed
  print "\nAll conversions have been completed. See if any errors exist."
