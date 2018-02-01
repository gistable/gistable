#!/usr/bin/env python
# marc-w.com
# Built and tested on Django 1.5

class BulkInsertManager(models.Manager):
    
    def _bulk_insert_ignore(self, create_fields, values, print_sql=False):
        '''
        Bulk insert/ignore
        @param create_fields : list, required, fields for the insert field declaration
        @param values : list of tuples. each tuple must have same len() as create_fields
        @param print_sql : bool, opotional, print to screen for debugging. True required to
            to print exception
        Notes on usage :
            create_fields = ['f1', 'f2', 'f3']
            values = [
                (1, 2, 3),
                (4, 5, 6),
                (5, 3, 8)
            ]
        Example usage :
            modelName.objects._bulk_insert_ignore(
                create_fields,
                values
            )
        Remember to add to model declarations:
            objects = BulkInsertManager() # custom manager
        @return False on fail
        '''
        from django.db import connection, transaction
        cursor = connection.cursor()

        db_table = self.model._meta.db_table

        values_sql = []
        values_sql.append( "(%s)" % (','.join([ " %s " for i in range(len(create_fields))]),) ) # correct format
        
        base_sql = "INSERT IGNORE INTO %s (%s) VALUES " % (db_table, ",".join(create_fields))
        sql = """%s %s""" % (base_sql, ", ".join(values_sql))
        
        ## debugging
        #print '----'
        #print sql
        #print values
        #sys.stdout.flush()
        
        try:
            cursor.executemany(sql, values)
            if print_sql is True:
                try :
                    print cursor._last_executed
                except :
                    pass
            transaction.commit_unless_managed()
            return True
        except Exception as e:
            try :
                print cursor._last_executed
            except :
                pass
            if print_sql is True:
                print e
            return False

    def _bulk_insert_on_duplicate(self, create_fields, values, update_fields, print_sql=False):
        '''
        Bulk insert, update on duplicate key
        @param create_fields : list, required, fields for the insert field declaration
        @param values : list of tuples. each tuple must have same len() as create_fields
        @param update_fields : list, field names to update when duplicate key is detected
        @param print_sql : bool, opotional, print to screen. True required to to print exception
        @return False on fail
        Notes on usage :
            create_fields = ['f1', 'f2', 'f3']
            values = [
                (1, 2, 3),
                (4, 5, 6),
                (5, 3, 8)
            ]
        Example usage :
            modelName.objects._bulk_insert_ignore(
                create_fields,
                values
            )
        Usage notes for update_fields :
            update_fields = ['f1', 'f2']
            where f1, f2 are not part of the unique declaration and represent
                fields to be updated on duplicate key
        Remember to add to model declarations:
            objects = BulkInsertManager() # custom manager
        '''
        from django.db import connection, transaction
        cursor = connection.cursor()

        db_table = self.model._meta.db_table

        values_sql = []
        values_sql.append( "(%s)" % (','.join([ " %s " for i in range(len(create_fields))]),) )
        
        base_sql = "INSERT INTO %s (%s) VALUES " % (db_table, ",".join(create_fields))
        
        duplicate_syntax = 'ON DUPLICATE KEY UPDATE ' # left side
        comma = len(update_fields) # verbose placement of comma
        for f in update_fields :
            comma = comma-1
            duplicate_syntax = duplicate_syntax+" "+f+'= values(%s)'% (f)
            if comma > 0 : # place a comma
                duplicate_syntax = duplicate_syntax+','
        
        sql = """%s %s %s""" % (base_sql, ", ".join(values_sql), duplicate_syntax)
        
        ## debugging
        #print '----'
        #print sql
        #print values
        #sys.stdout.flush()
        
        try:
            cursor.executemany(sql, values)
            if print_sql is True:
                try :
                    print cursor._last_executed
                except :
                    pass
            transaction.commit_unless_managed()
            return True
        except Exception as e:
            try :
                print cursor._last_executed
            except :
                pass
            if print_sql is True :
                print e
            return False