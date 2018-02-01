#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlsoup import SQLSoup as sql
from sys import argv

DIGRAPH = """digraph structs {
    graph [
       rankdir= "LR"
       bgcolor=white
    ]
    
    node [ 
        fontsize=12 
        shape=record 
    ]
    
    %s
}
"""

db=sql(argv[1])

print "introspecting %s" %  argv[1]
to_scan = db.engine.table_names()
vertices = []
nodes = dict()
interesting = set([])
fk_count = 0
field_count = 0

while to_scan:
    node_str = ''
    try:
        table_name = to_scan.pop()
        table = getattr(db,table_name)
        node_str += """
    %s [ 
        label="%s""" % (table_name, table_name)
        has_fk=False
        for c in table._table.c:
            node_str += "|<%s>%s" % (c.name, c.name)
            field_count += 1
            #print "adding %s" % c.name
            if c.foreign_keys:
                for fk in c.foreign_keys:
                    interesting |= { table_name, fk.column.table.name, }
                    fk_count+=1
                    # if you want to make a progressive scan around a table vicinity
                    #to_scan += [ fk.column.table.name ]
                    vertices += [ (
                        ":".join([table_name, c.name]),  
                        ":".join([ fk.column.table.name, fk.column.name]),
                        fk.name or '""'),
                    ]
                    
        nodes[table_name] = """%s"
        color=%%s
        bgcolor=%%s
    ]""" % node_str
            
    except Exception as e:
        print "problem with %r" % table_name
        print repr(e)
        

to_print = ""
for node in nodes:
    #to_print += node % (("grey","grey"), ("black", "white"))[node in interesting]
    to_print += nodes[node] % (("grey","grey"), ("black", "white"))[node in interesting]

    
for v in vertices:
    to_print+="""
    %s -> %s [ label=%s ]
""" % v
to_print = DIGRAPH % to_print
print "nb col = %r" % field_count
print "nb fk = %r" % fk_count

with open("out.dot", "w") as f: f.write(to_print)