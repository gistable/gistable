from collections import namedtuple
from pymongo import MongoClient
from flask import request
from core.web.site import app
from core.web.site.views_master import *
import json

'''
$('#companies').dataTable( {
            "bProcessing": true,
            "bServerSide": true,
            "sPaginationType": "full_numbers",
            "bjQueryUI": true,
            "sAjaxSource": "/_retrieve_server_data"
});
 
'''
# create an app.route for your javascript. see above ^ for javascript implementation
@app.route("/_retrieve_server_data")
def get_server_data():
 
    columns = [ 'column_1', 'column_2', 'column_3', 'column_4']
    index_column = "_id"
    collection = "collection_name"
 
    results = DataTablesServer(request, columns, index_column, collection).output_result()
     
    # return the results as a string for the datatable
    return json.dumps(results)

# translation for sorting between datatables and mongodb
order_dict = {'asc': 1, 'desc': -1}

class DataTablesServer(object):
 
    def __init__( self, request, columns, index, collection):
 
        self.columns = columns
        self.index = index
        self.collection = collection
         
        # values specified by the datatable for filtering, sorting, paging
        self.request_values = request.values
         
        # connection to your mongodb (see pymongo docs). this is defaulted to localhost
        self.dbh = MongoClient()
 
        # results from the db
        self.result_data = None
         
        # total in the table after filtering
        self.cardinality_filtered = 0
 
        # total in the table unfiltered
        self.cardinality = 0
 
        self.run_queries()

    def output_result(self):
                
        output = {}
        output['sEcho'] = str(int(self.request_values['sEcho']))
        output['iTotalRecords'] = str(self.cardinality)
        output['iTotalDisplayRecords'] = str(self.cardinality_filtered)
        aaData_rows = []
 
        for row in self.result_data:
            aaData_row = []
            for i in range( len(self.columns) ):
 
                aaData_row.append(row[ self.columns[i] ].replace('"','\\"'))
             
            # add additional rows here that are not represented in the database
            # aaData_row.append(('''<input id='%s' type='checkbox'></input>''' % (str(row[ self.index ]))).replace('\\', ''))
 
            aaData_rows.append(aaData_row)
 
        output['aaData'] = aaData_rows
 
        return output

    def run_queries(self):
 
        # 'mydb' is the actual name of your database
        mydb = self.dbh.mydb
 
        # pages has 'start' and 'length' attributes
        pages = self.paging()
         
        # the term you entered into the datatable search
        _filter = self.filtering()
         
        # the document field you chose to sort
        sorting = self.sorting()
 
        # get result from db to display on the current page
        self.result_data = list(mydb[self.collection].find(spec = _filter,
                                                           skip = pages.start,
                                                           limit = pages.length,
                                                           sort = sorting))
 
        # length of filtered set  
        self.cardinality_filtered = len(list(mydb[self.collection].find(spec = _filter)))
        
        # length of all results you wish to display in the datatable, unfiltered
        self.cardinality = len(list( mydb[self.collection].find()))
 
    def filtering(self):
         
        # build your filter spec
        _filter = {}
        if ( self.request_values.has_key('sSearch') ) and ( self.request_values['sSearch'] != "" ):
             
            # the term put into search is logically concatenated with 'or' between all columns
            or_filter_on_all_columns = []
             
            for i in range( len(self.columns) ):
                column_filter = {}
                # case insensitive partial string matching pulled from user input
                column_filter[self.columns[i]] = {'$regex': self.request_values['sSearch'], '$options': 'i'}
                or_filter_on_all_columns.append(column_filter)
            
            _filter['$or'] = or_filter_on_all_columns
        
        # individual column filtering - uncomment if needed
        
        #and_filter_individual_columns = []
        #for i in range(len(columns)):
        #    if (request_values.has_key('sSearch_%d' % i) and request_values['sSearch_%d' % i] != ''):
        #        individual_column_filter = {}
        #        individual_column_filter[columns[i]] = {'$regex': request_values['sSearch_%d' % i], '$options': 'i'}
        #        and_filter_individual_columns.append(individual_column_filter)

        #if and_filter_individual_columns:
        #    _filter['$and'] = and_filter_individual_columns
       
        return _filter
  
    def sorting(self):
                
        order = []
        # mongo translation for sorting order
        if ( self.request_values['iSortCol_0'] != "" ) and ( self.request_values['iSortingCols'] > 0 ):
            
            for i in range( int(self.request_values['iSortingCols']) ):
                # column number
                column_number = int(self.request_values['iSortCol_'+str(i)])
                # sort direction
                sort_direction = self.request_values['sSortDir_'+str(i)]
                
                order.append((self.columns[column_number], order_dict[sort_direction]))
        
        return order
 
    def paging(self):
                
        pages = namedtuple('pages', ['start', 'length'])
        
        if (self.request_values['iDisplayStart'] != "" ) and (self.request_values['iDisplayLength'] != -1 ):
            pages.start = int(self.request_values['iDisplayStart'])
            pages.length = int(self.request_values['iDisplayLength'])
        
        return pages