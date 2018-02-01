class DatabaseWrapper(BaseDatabaseWrapper):
    SEARCH_PAGE_SIZE=999

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.charset = "utf-8"
        self.creation = DatabaseCreation(self)
        self.features = DatabaseFeatures(self)
        if django.VERSION > (1, 4):
            self.ops = DatabaseOperations(self)
        else:
            self.ops = DatabaseOperations()
        self.settings_dict['SUPPORTS_TRANSACTIONS'] = False
        self.pool = self.settings_dict.get('POOL', None)

    def close(self):
        if self.connection:
            grn = gevent.getcurrent()
            try:
                name = grn._run.__name__ if not hasattr(grn._run, 'f') else grn._run.f.__name__
            except AttributeError:
                name = "-"
            if self.pool:
                
                conn_id = id(self.connection.get_connection().obj)
                self.connection.release()
                log.info("--RELEASE-- connID[{}] thread[{}] func[{}] {}".format(conn_id, hex(id(grn)), name, self.pool.getstats()))
                self.connection = None
            else:
                global closes
                closes += 1
                conn_id = id(self.connection.obj)
                log.info("--CLOSE-- connID[{}] thread[{}] func[{}] ({}/{})".format(conn_id, hex(id(grn)), name, opens, closes))
                self.connection.unbind_s() 
                self.connection = None

    def _commit(self):
        pass

    def _cursor(self):
        if self.connection is None:
            grn = gevent.getcurrent()
            try:
                name = grn._run.__name__ if not hasattr(grn._run, 'f') else grn._run.f.__name__
            except AttributeError:
                name = "-"
            if self.pool:
                
                self.connection = self.pool.connection()
                conn_id = id(self.connection.get_connection().obj)
                log.info("+++LEASE+++ connID[{}] thread[{}] func[{}] {}".format(conn_id, hex(id(grn)), name, self.pool.getstats()))
                
            else:
                self.connection = ldap.initialize(self.settings_dict['NAME'])
                self.connection.simple_bind_s(
                    self.settings_dict['USER'],
                    self.settings_dict['PASSWORD'])
                conn_id = id(self.connection.obj)
                global opens
                opens += 1
                log.info("--OPEN-- connID[{}] thread[{}] func[{}] ({}/{})".format(conn_id, hex(id(grn)), name, opens, closes))
        return DatabaseCursor(self.connection)

    def _rollback(self):
        pass

    def add_s(self, dn, modlist):
        cursor = self._cursor()
        try:
            return cursor.connection.add_s(dn.encode(self.charset), modlist)
        finally:
            if self.pool:
                self.close()

    def delete_s(self, dn):
        cursor = self._cursor()
        try:
            return cursor.connection.delete_s(dn.encode(self.charset))
        finally:
            if self.pool:
                self.close()
        

    def modify_s(self, dn, modlist):
        cursor = self._cursor()
        try:
            return cursor.connection.modify_s(dn.encode(self.charset), modlist)
        finally:
            if self.pool:
                self.close()

    def rename_s(self, dn, newrdn):
        cursor = self._cursor()
        try:
            return cursor.connection.rename_s(dn.encode(self.charset), newrdn.encode(self.charset))
        finally:
            if self.pool:
                self.close()

    def search_s(self, base, scope, filterstr='(objectClass=*)',attrlist=None):
        ''' PHF changed to allow for empty filterstr.  The enabled DNs to be searchable.'''
        cursor = self._cursor()
        try:
            if filterstr:
                results = cursor.connection.search_s(base, scope, filterstr, attrlist)
            else:
                results = cursor.connection.search_s(base, ldap.SCOPE_BASE, attrlist=attrlist)
            output = []
            for dn, attrs in results:
                output.append((dn.decode(self.charset), attrs))
            return output
        finally:
            if self.pool:
                self.close()