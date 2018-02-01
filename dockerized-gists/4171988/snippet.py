## I'm working on a project using Flask to access a database and then 
## pass on query data to a client where the data will be graphed  
## in the browser. 
## I wanted to enable users to retrieve the graph data
## in a csv file after clicking a button on the client. 
## This is a generalized version of how I did it:

# imports other than Flask
import csv
from sqlalchemy import create_engine
from flask import make_response

@app.route('/GetDataFile',methods=['get'])
def get_branch_data_file():
    connection = engine.connect()
    data_for_csv = []
    data = connection.execute("... MySQL Query ... ")
    (file_basename, server_path, file_size) = create_csv(data)

    return_file = open(server_path+file_basename, 'r')
    response = make_response(return_file,200)
    response.headers['Content-Description'] = 'File Transfer'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_basename
    response.headers['Content-Length'] = file_size
    return response

## function to create csv from the SQLAlchemy query response object

def create_csv(data):
    """ returns (file_basename, server_path, file_size) """
    file_basename = 'output.csv'
    server_path = '/directory/subdirectory'
    w_file = open(server_path+file_basename,'w')
    w_file.write('your data headers separated by commas \n')
    
    for row in data:
        row_as_string = str(row)
        w_file.write(row_as_string[1:-1] + '\n') ## row_as_string[1:-1] because row is a tuple

    w_file.close()

    w_file = open(server_path+file_basename,'r')
    file_size = len(w_file.read())
    return file_basename, server_path, file_size