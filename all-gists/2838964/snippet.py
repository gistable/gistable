import csv
import sqlite3 as lite
import subprocess
from itertools import chain
from time import time
import sys
#import logging
#logging.basicConfig(level=logging.DEBUG)
#


#I want to create a database with a table for the meta data,
#and then one table for every time increment.

def convert(value):
    '''takes a string, tries to convert it to an int, then a float, then
    defaults to string if both give an error. Returns a tuple of the SQLite 
    type and function for conversion'''
    tests = [("INTEGER", int), ("REAL", float)]
    for lite_type, test in tests:
        try:
            test(value)
            return lite_type, test
        except ValueError:
            continue
    return "STRING", str # All other heuristics failed it is a string



def make_table(header, types,  cursor, tablename):
    '''Makes a new table with `cursors`, with column names as specified 
    in `header`, data types as specified by `types`, and name specified by `tablename`'''
    table_fields = [" ".join(v) for v in zip(header, types)]
    #table_fields sets up the fields and their types for this table.
    #Of course, since we name the tables by time, we don't need to keep that variable.
    creation_string = "CREATE TABLE %(tablename)s (%(args)s)" % {
                       'args': ", ".join(table_fields),
                       'tablename': tablename}
    cursor.execute(creation_string)

def put_in(dictionary, c, conn):
    '''Inserts values of dictionary into tables with names equal to the keys of the dictionary. The database has `conn` as the connection, and `c` as a cursor, '''
    for name in dictionary.keys(): 
        query_command = 'INSERT INTO '+ name +' VALUES (%s)' % ', '.join(['?']*len(dictionary[name][0]))
        c.executemany(query_command, iter(dictionary[name]))
    conn.commit()

def make_DB(data_file, data_base_name, block_size):
    '''This function runs through a data_file, assumed to be csv,
    and makes a sqlite database out of it Currently it is tailored to the 
    '''
    t0 = time() #time the operation.
    with open(data_file) as f, lite.connect(data_base_name) as conn:
        #connecting:
        lines = csv.reader(f) 
        c = conn.cursor()

        #Initializing
        header = lines.next() #Column names
        c.execute("SELECT name FROM sqlite_main WHERE type='table';")
        last_tables = set([ '['+ x[0] +']' for x in c.fetchall()]) #Keeping track of tables currently in db.

        #Finding types:
        first = lines.next() #The first element in the whole csv.
        sample = first[:] #this is going to be used for type matching.
        sample.pop(2) #don't match third element, it's going to be table name.
        types, conv = zip(*[convert(entry) for entry in sample]) #adding a `*` actually unzips. see above for `convert`.

        toPut = {} #Initialize variables
        line_counter = 1

        renew_lines = chain([first], lines) #Put the first line back on first.

        for line in renew_lines:
            date_time = line.pop(2) #the second element is the date
            table_name = "".join(["[", date_time.replace(" ", "_"), "]"]) #convert to valid table name
            
            if not table_name in last_tables: #This keeps track of tables. #If it's not in the db, add it, add it to list keeping track of this.
                make_table(header, types, c, table_name)
                last_tables.add(table_name)

            if not table_name in toPut.keys():
                toPut[table_name] = [] #Initialize the array

            #No matter what, the line goes into the table withe corresponding name
            toPut[table_name].append( tuple([g(x) for (g, x) in zip(conv, line)] )) #The data just gets converted to the right type before input.
            #setting correct types for everybody
            if not line_counter % block_size: #Check if 0 modulo block_size, if so, report current location, call put_in,
                sys.stdout.write("writing to tables " + toPut.keys() +". \r")
                sys.stdout.flush()
                put_in(toPut, c, conn) #put_in writes dictionary to table.
                toPut = {} 

            line_counter += 1 
            sys.stdout.write("now on line number " + str(line_counter) + ".    \r")
            sys.stdout.flush() 
        put_in(toPut, c, conn) #Eating the leftovers, so to speak. The number of lines probably isn't a multiple of the block size, 
                               #so this puts any leftovers into the database.
    print "\n", time() - t0

#make_DB("../metaStatus-3-7.csv", "VAST2.db", 500000) #This is the call I make on my system.
