from django.db import connections
from django.db.models.query import QuerySet

class ApproxCountQuerySet(QuerySet): 
    """Counting all rows is very expensive on large Innodb tables. This 
    is a replacement for QuerySet that returns an approximation if count()
    is called with no additional constraints. In all other cases it should
    behave exactly as QuerySet.
    
    Only works with MySQL. Behaves normally for all other engines.
    """ 
 
    def count(self): 
        # Code from django/db/models/query.py 
         
        if self._result_cache is not None and not self._iter: 
            return len(self._result_cache) 

        is_mysql = 'mysql' in connections[self.db].client.executable_name.lower()
 
        query = self.query 
        if (is_mysql and not query.where and 
                query.high_mark is None and 
                query.low_mark == 0 and 
                not query.select and  
                not query.group_by and 
                not query.having and 
                not query.distinct): 
            # If query has no constraints, we would be simply doing
            # "SELECT COUNT(*) FROM foo". Monkey patch so the we 
            # get an approximation instead. 
            cursor = connections[self.db].cursor() 
            cursor.execute("SHOW TABLE STATUS LIKE %s", 
                    (self.model._meta.db_table,)) 
            return cursor.fetchall()[0][4]
        else: 
            return self.query.get_count(using=self.db)