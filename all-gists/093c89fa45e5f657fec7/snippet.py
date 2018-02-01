import os
import urllib
import urllib2
import base64
import json
import sys
import argparse
try:
    import requests
except ImportError:
    print 'The requests package is required: http://docs.python-requests.org/en/latest/user/install/#install'
    sys.exit()
 
class CartoDB:
    def __init__(self, options):
        # do stuff
        self.options = options
        self.api_url = "https://%s.cartodb.com/api/v2/sql" % (self.options['u'])
        self.import_url = "https://%s.cartodb.com/api/v1/imports/?api_key=%s" % (self.options['u'], self.options['k'])
        self.new_tables = []
        self.internal_columns = ['created_at', 'updated_at', 'the_geom', 'the_geom_webmercator', 'cartodb_id']
        self.type_map = {'string':'text', 'boolean': 'boolean', 'date': 'timestamp', 'number':'numeric'}
    def _log(self, message):
        if self.options['verbose'] == True:
            print message
    def _error(self, error):
        print error
        sys.exit()
    def sql_api(self, sql):
        # execute sql request over API
        params = {
            'api_key' : self.options["k"],
            'q'       : sql
        }
        r = requests.get(self.api_url, params=params)
        return r.json()
    def upload(self):
        # import a file
        # see https://gist.github.com/lbosque/5876697
        # returns new table name
        r = requests.post(self.import_url, files={'file': open(self.options['f'], 'rb')})
        data = r.json()
        if data['success']!=True:
            self._error("Upload failed")
        complete = False
        last_state = ''
        while not complete: 
            import_status_url = "https://%s.cartodb.com/api/v1/imports/%s?api_key=%s" % (self.options['u'], data['item_queue_id'], self.options['k'])
            req = urllib2.Request(import_status_url)
            response = urllib2.urlopen(req)
            d = json.loads(str(response.read()))
            if last_state!=d['state']:
                last_state=d['state']
                if d['state']=='uploading':
                    self._log('Uploading file...')
                elif d['state']=='importing':
                    self._log('Importing data...')
                elif d['state']=='complete':
                    complete = True
                    self._log('Table "%s" created' % d['table_name'])
            if d['state']=='failure':
                self._error(d['get_error_text']['what_about'])    
        self.new_tables.append(d['table_name'])
        return d['table_name']
 
    def columns(self, table):
        sql = "SELECT * FROM %s LIMIT 0" % table 
        data = self.sql_api(sql)
        return data['fields']
 
    def add_column(self, table, name, coltype):
        sql = "ALTER TABLE %s ADD COLUMN %s %s" % (table, name, coltype)
        data = self.sql_api(sql)
        return True
 
    def overwrite(self, append=False):
        # upload new data
        new_table = self.upload()
        source_columns = self.columns(new_table)
        target_columns = self.columns(self.options['t'])
        insert_cols = {}
        alter_cols = []
        for c in source_columns.keys():
            if c in self.internal_columns:
                source_columns.pop(c, None)
            else:
                if c not in target_columns.keys():
                    insert_cols[c] = self.type_map[source_columns[c]['type']]
                    alter_cols.append(c)
                else: 
                    insert_cols[c] = self.type_map[target_columns[c]['type']]
        for c in alter_cols:
            self.add_column(self.options['t'], c, insert_cols[c])
        select_list = []
        for c,t in insert_cols.items():
            select_list.append( "%s::%s" % (c,t))
        sql = "INSERT INTO %s (the_geom, %s) " % (self.options['t'], ','.join(insert_cols.keys()))
        sql += "SELECT the_geom, %s FROM %s; " % (','.join(select_list), new_table)
        sql += "DROP TABLE %s" % new_table
        self._log("Writing data to %s and droppping %s" % (self.options['t'],new_table))
        if append==False:
            sql = "DELETE FROM %s; %s " % (self.options['t'], sql)
        data = self.sql_api(sql)
        if 'error' in data.keys():
            self._log('Overwrite failed, cleaning-up')
            sql = "DROP TABLE %s" % new_table
            self.sql_api(sql)
            return False
        else:
            return True
 
    def drop_table(self):
        # drop a table '
        self._log("Dropping table %s"  % self.options['t'])
        sql = "DROP TABLE %s" % self.options['t']
        data = self.sql_api(sql)
        if 'error' in data.keys():
            self._error(data['error'])
        return True
    
    def clear_rows(self):
        # clear all rows from a table
        self._log("Deleting all rows")
        sql = "DELETE FROM %s" % self.options['t']
        data = self.sql_api(sql)
        if 'error' in data.keys():
            self._error(data['error'])
        return True
 
    def export_table(self):
        self._log("Exporting new %s" % self.options['m'])
        params = {"format": self.options['m'], "api_key": self.options["k"],"q": "SELECT * FROM %s" % self.options["t"]}
        r = requests.get(self.api_url, params=params, stream=True)
        with open(self.options['l'], 'wb') as fd:
            for chunk in r.iter_content(10):
                fd.write(chunk)
        return True
    def clean_table(self):
        # clean up table for speed
        self._log("Cleaning up unused space")
        sql = "VACUUM FULL %s" % self.options['t']
        data = self.sql_api(sql)
        if 'error' in data.keys():
            self._error(data['error'])
        self._log("Optimizing existing indexes")
        sql = "ANALYZE %s" % self.options['t']
        data = self.sql_api(sql)
        if 'error' in data.keys():
            self._error(data['error'])
        return True
        
if __name__ == "__main__":
 
    SUPPORTED_METHODS = {
        'import' : {
            "description": "Import a file to create a new table",
            "requirements": ["f","k","u"],
            "example": "python cartodb-utils.py import -f myfile.csv -k myapikey -u myusername"
        },
        'overwrite' : {
            "description": "Overwrite an existing table with data from a file",
            "requirements": ["f","k","u","t"],
            "example": "python cartodb-utils.py overwrite -f myfile.csv -t some_existing_table -k myapikey -u myusername"
        },
        'append' : {
            "description": "Append rows to an existing table from a file",
            "requirements": ["f","k","u","t"],
            "example": "python cartodb-utils.py append -f myfile.csv -t some_existing_table -k myapikey -u myusername"
        },
        'clear' : {
            "description": "Clear all rows from an existing table",
            "requirements": ["k","u","t"],
            "example": "python cartodb-utils.py clear -t some_existing_table -k myapikey -u myusername"
        },
        'drop' : {
            "description": "Completely drop an existing table",
            "requirements": ["k","u","t"],
            "example": "python cartodb-utils.py drop -t some_existing_table -k myapikey -u myusername"
        },
        'export' :{
            "description": "Export an existing table to a local file (default GeoJSON)",
            "requirements": ["k","u","t","l"],
            "example": "python cartodb-utils.py export -t some_existing_table -m CSV -l local_file.csv -k myapikey -u myusername"
        },
        'clean' : {
            "description": "Vacuum and analyze a table for speed",
            "requirements": ["k","u","t"],
            "example": "python cartodb-utils.py clean -t some_existing_table -k myapikey -u myusername"
        }
    }
    parser = argparse.ArgumentParser(description="CartoDB Python Utility")
 
    parser.add_argument('method', nargs="?", help='e.g. %s' % ','.join(SUPPORTED_METHODS.keys()))
 
    parser.add_argument('-f', '--file', dest='f', help='Source file')
    parser.add_argument('-l', '--local', dest='l', help='Local file')
    parser.add_argument('-m', '--format', default="GeoJSON", dest='m', help='Export file format')
    parser.add_argument('-u', '--user', dest='u', help='CartoDB username')
    parser.add_argument('-k', '--key', dest='k', help='CartoDB account API Key')
    parser.add_argument('-t', '--target', dest='t', help='Target table')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action="store_true", help='Verbose output if included')
 
    args = parser.parse_args()
    options = vars(args)
 
    def success(message):
        print 'SUCCESS', message
    def failure(message):
        print 'FAILURE', message
    m = args.method.lower()
    if m in SUPPORTED_METHODS.keys():
        for d in SUPPORTED_METHODS[m]["requirements"]:
            if options[d] is None:
                print "Arguement -%s is required\n\n%s\n\ndescription:\t%s\nrequired args:\t%s\nexample:\t%s" % (d,m,SUPPORTED_METHODS[m]['description'],SUPPORTED_METHODS[m]['requirements'],SUPPORTED_METHODS[m]['example'])
                sys.exit()
 
        cartodb = CartoDB(options)
        if args.method.lower() == 'import':
            new_table = cartodb.upload()
            success(new_table)
        if args.method.lower() == 'overwrite':
            status = cartodb.overwrite()
            if status == True: 
                success('Table data replaced')
        if args.method.lower() == 'append':
            status = cartodb.overwrite(True)
            if status == True: 
                success('Data appended to table')
        if args.method.lower() == 'clean':
            status = cartodb.clean_table()
            if status == True: 
                success('Cleaned table')
        if args.method.lower() == 'drop':
            status = cartodb.drop_table()
            if status == True: 
                success('Dropped table')
        if args.method.lower() == 'clear':
            status = cartodb.clear_rows()
            if status == True: 
                success('Cleared all rows from table')
        if args.method.lower() == 'export':
            status = cartodb.export_table()
            if status == True: 
                success('Exported table to %s' % options['l'])