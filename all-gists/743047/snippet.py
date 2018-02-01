#!/usr/bin/env python
from optparse import OptionParser
from xml.dom.minidom import parse
import os
import sqlite3


datatypeMap = {
  'integer': 'INT',
  'datetime': 'DATETIME',
  'boolean': 'BOOLEAN'
}

defaultDataType = 'TEXT'


def get_xml_doms(directory):
  result = []
  for filename in directory:
    if filename.endswith('.xml'):
      dom = parse(filename)
      result.append(dom)
  return result  

def yield_db_schema(dbDef):
  result = ''
  for (table, tableDef) in dbDef.items():
    result += create_table(table, tableDef) 
    
  return result

def exec_create_schema(dbDef, conn, db):
  for (table, tableDef) in dbDef.items():
    create = create_table(table, tableDef) 
    db.execute(create)
    
def yield_inserts(recordSet):
  inserts = ''
  for (table, rows) in recordSet.items():
    for row in rows:
      fields = "\'" + '\', \''.join(row.keys()) + "\'"
      data = "\'" + '\', \''.join(row.values()) + "\'"
      if fields != "''":
        inserts += "INSERT INTO \'%s\' (%s) VALUES (%s);\n" % (table, fields, data)
  
  return inserts
  
def exec_insert(recordSet, conn, db):
  for (table, rows) in recordSet.items():
    for row in rows:
        
      fields = "\'" + '\', \''.join(row.keys()) + "\'"
      data = "\'" + '\', \''.join(row.values()) + "\'"
      if len(row.keys()) >0:
        marklist = ["?"] * len(row.keys())
        marks = ', '.join(marklist)
          
        insert = "INSERT INTO \'%s\' (%s) VALUES (%s)" %  (table, fields, marks)
        values = tuple(row.values())
        db.execute(insert, values)
        conn.commit()
        

def create_table(table, tableDef):
  fields = []
  begin = 'CREATE TABLE \'%s\' ( \n' % table
  for field, fieldDef in tableDef.items():
    fields.append(create_field(field, fieldDef))
  end = '\n);\n\n'  
  result = begin + ',\n'.join(fields) + end
  
  return result

def create_field(field, fieldDef):
  if fieldDef.has_key(u'type'):
    datatype =  fieldDef.get(u'type')
  else:
    datatype = defaultDataType
  
  return "  '%s' %s" % (field, datatype) 

def collect_structure(doms):
  db = {}
  records = {}
  for dom in doms:
    db = gen_db_struct(dom.childNodes, db)
 
  return db
  
def collect_data(dbDef, doms):
  recordset = {}
  for dom in doms:
    for (table, fieldDef) in dbDef.items():
      if not recordset.has_key(table):
        recordset[table] = []
      for row in dom.getElementsByTagName(table):
        record = {}
        for (column, _) in fieldDef.items():
          for node in row.getElementsByTagName(column):
            if node.hasChildNodes():
              for item in node.childNodes:
                if hasattr(item, 'data'):
                  if len(item.data.strip()) > 0:
                    record[column] = item.data
              
        recordset[table].append(record)
  
  return recordset
              

def gen_db_struct(nodeList, db = {}):
  for node in nodeList:
    if not node.hasChildNodes() and node.parentNode.parentNode.nodeName != '#document':
      # a new field of data
      field = node.parentNode
      fieldName = field.nodeName
      table = field.parentNode
      tableName = table.nodeName
        
      if not db.has_key(tableName):
        db[tableName] = {}
  
      db[tableName][fieldName] = {}

      if field.hasAttributes():
        for (Key, Value) in field.attributes.items():
          if Key != u'type' and Value != u'array':
            db[tableName][fieldName][Key] = datatypeMap[Value]   
    else:
      gen_db_struct(node.childNodes, db)
      
  return db

def run(inputDir, outputFile):
  files = []
  for filename in os.listdir(inputDir):
    files.append(os.path.join(inputDir, filename))
    
  domList = get_xml_doms(files)
  dbDef = collect_structure(domList)
  records = collect_data(dbDef, domList)
  conn = sqlite3.connect(outputFile)
  db = conn.cursor()
  exec_create_schema(dbDef, conn, db)
  exec_insert(records, conn, db)
  db.close()
  
def main():
  usage = "usage: %prog [options] /path/to/dir/with/xml"
  parser = OptionParser(usage)
  parser.add_option("-f", "--file", dest="outputFile", default = 'xmlsqlite.db3',
                    help="Specify the filename for the sqlite database.  It will be created if it does not exist [Default: xmlsqlite.db3]")

  (options, args) = parser.parse_args()
  if len(args) != 1:
      parser.error("incorrect number of arguments")
  
  inputDir = os.path.abspath(os.path.expanduser(args[0]))
  run(inputDir, options.outputFile)

  
if __name__ == "__main__": main()