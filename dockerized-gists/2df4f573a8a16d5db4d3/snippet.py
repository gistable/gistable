#!/usr/bin/python
# Filename: sas_export.py
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 06 18:40:09 2015
@author: David Carlson
modified version for sas7bdat 2.0.1 of Charlie Huang version at:
http://www.sasanalysis.com/2014/08/python-extension-functions-to-translate.html
"""

import sqlite3
import glob
import sas7bdat
import logging
import os
import itertools
import time

def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))
 
class SASexport(sas7bdat.SAS7BDAT):

    def head(self, n=5):
        for i, row in enumerate(self):
            if i != 0:
                print row
            if i > n:
                break
               
    def to_sqlite(self, 
                  sqlitedb=None, 
                  step_size=100000, 
                  batch_size=10000, 
                  scrub_function = None):
                      
        if sqlitedb is None:
            file_name = self.properties.filename.split('.')[0]
            sqlitedb = os.path.join(os.path.dirname(self.path), 
                                    file_name + '.db3')
                                    
        if not isinstance(sqlitedb, str):
            print('not a valid database path: ' + sqlitedb)
        self.logger.debug('saving as: %s', sqlitedb)
        
        cols = self.columns
        strs = [''] * len(cols)
        
        for i, n in enumerate(cols):
            if n.type == "number":
                strs[i] = n.name + ' real'
            else:
                strs[i] = n.name + ' varchar({})'.format(n.length)
                
        table = self.properties.name
        
        cmd1 = "CREATE TABLE {} ({})".format(table, ', '.join(strs))
        cmd2 = 'INSERT OR IGNORE INTO {} VALUES ( {} )'.format(
            table,
            ','.join(['?']*len(cols)))
                        
        conn = sqlite3.connect(sqlitedb)
        conn.isolation_level = None
        c = conn.cursor()         
        
        success=True
        t = time.time()
        i = 0  
        
        try:
            for chunk in split_seq(self, batch_size):               
                if i == 0:
                    c.execute('DROP TABLE IF EXISTS {}'.format(table))
                    c.execute(cmd1)                    
                c.execute('begin')           
                for line in chunk:
                    if len(line) != (self.properties.column_count or 0):
                        msg = 'parsed line into %s columns but was ' \
                              'expecting %s.\n%s' %\
                              (len(line), self.properties.column_count, line)
                        self.logger.error(msg)
                        success = False
                        if self.logger.level == logging.DEBUG:
                            raise sas7bdat.ParseError(msg)
                        break                                                          
                    if not i % step_size:
                        self.logger.info(
                            '%.1f%% complete',
                            float(i) / self.properties.row_count * 100.0
                            )                    
                    try:
                        if i != 0:
                            if scrub_function != None:
                                scrub_function(line)
                            c.execute(cmd2, line)
                    except IOError:
                        self.logger.warn('wrote %s lines before interruption', i)
                        break                    
                    i += 1                                       
                c.execute('commit')                                      
            self.logger.info(u'\u27f6 [%s] wrote %s of %s lines',
                             os.path.basename(sqlitedb), i-1,
                             self.properties.row_count or 0)
            self.logger.info('\n time taken: %.3f sec', (time.time()-t))
            
        finally:   
            conn.commit()
            c.close()          

        return success   

 
class SASbatchexport:
    def __init__(self, directory):
        if directory is None or not isinstance(directory, str):
            raise ValueError('SAS library path has to be specified')
        self.directory = directory
    def to_sqlitedb(self, dest=None):
        """Export all SAS data sets to a SQLite database"""
        if dest is None or not isinstance(dest, str):
            print 'The output SQLite db will be name as SASOUTPUT.db'
            dest = 'SASOUTPUT.db'
        s = self.directory + '/*.sas7bdat'
        for sasfile in glob.glob(s):
            _data = SASexport(sasfile)
            _data.to_sqlite(dest)
            print 'SAS dataset {} has been successfully exported'.format( \
                _data.header.dataset)