'''
A simple tool for exporting from a PostGIS table to GeoJSON and TopoJSON. Assumes Python 2.7+, 
psycopg2, and TopoJSON are already installed and in your PATH.

Adapted from Bryan McBride's PHP implementation 
(https://gist.github.com/bmcbride/1913855/) 
by John Czaplewski | jczaplew@gmail.com | @JJCzaplewski

TODO:
- Add argument for SRS
- Clean up

'''
import argparse
import psycopg2
import json
import subprocess

parser = argparse.ArgumentParser(
	description="Create a GeoJSON from a PostGIS query.",
	epilog="Example usage: python postgis2geojson.py -d awesomeData -h localhost -u user -p securePassword -t table -f id name geom -w 'columnA = columnB' -o myData --topojson")

parser.add_argument("-d", "--database", dest="database",
	type=str, required=True,
	help="The database to connect to")

# Python doesn't let you use -h as an option for some reason
parser.add_argument("-H", "--host", dest="host",
	default="localhost", type=str,
	help="Database host. Defaults to 'localhost'")

parser.add_argument("-u", "--user", dest="user",
	default="postgres", type=str,
	help="Database user. Defaults to 'postgres'")

parser.add_argument("-p", "--password", dest="password",
	type=str, required=True,
	help="Password for the database user")

parser.add_argument("-t", "--table", dest="table",
	type=str, required=True,
	help="Database table to query")

parser.add_argument("-f", "--fields", dest="fields",
	nargs="+",
	help="Fields to return separated by a single space. Defaults to *")

parser.add_argument("-g", "--geometry", dest="geometry",
	default="geom", type=str, 
	help="Name of the geometry column. Defaults to 'geom'")

parser.add_argument("-w", "--where", dest="where",
	type=str,
	help="Optional WHERE clause to add to the SQL query")

parser.add_argument("-o", "--output", dest="file",
	default="data", type=str,
	help="Output file name without extension. Defaults to 'data.geojson'")

parser.add_argument("--topojson", dest="topojson",
	action="store_true",
	help="Use if you would also like a copy of the data as TopoJSON")

arguments = parser.parse_args()

def getData():
	# Connect to the database
	try:
		conn = psycopg2.connect("dbname=" + arguments.database + " user=" + arguments.user + " host=" + arguments.host + " password="+ arguments.password)
	except:
		print "Unable to connect to the database. Please check your options and try again."
		return

	# Create a cursor for executing queries
	cur = conn.cursor()

	# Start building the query
	query = "SELECT "

	# If a list of fields were provided, add those
	if isinstance(arguments.fields, list):
		for each in arguments.fields:
			query += each + ", " 

	# Otherwise, just select everything
	else:
		query += "*, "

	query += "ST_AsGeoJSON(" + arguments.geometry + ") AS geometry FROM " + arguments.table

	# If a WHERE statement was provided, add that
	if arguments.where is not None:
		query += " WHERE " + arguments.where + ";"
	else:
		query += ";"

	# Execute the query
	try:
		cur.execute(query)
	except:
		print "Unable to execute query. Please check your options and try again."
		return

	# Retrieve the results of the query
	rows = cur.fetchall();

	# Get the column names returned
	colnames = [desc[0] for desc in cur.description]

	# Find the index of the column that holds the geometry
	geomIndex = colnames.index("geometry")

	# output is the main content, rowOutput is the content from each record returned
	output = ""
	rowOutput = ""
	i = 0

	# For each row returned...
	while i < len(rows):
		# Make sure the geometry exists
		if rows[i][geomIndex] is not None:
			# If it's the first record, don't add a comma
			comma = "," if i > 0 else ""
			rowOutput =  comma + '{"type": "Feature", "geometry": ' + rows[i][geomIndex] + ', "properties": {'
			properties = ""
			
			j = 0
			# For each field returned, assemble the properties object
			while j < len(colnames):
				if colnames[j] != 'geometry':
					comma = "," if j > 0 else ""
					properties +=  comma + '"' + colnames[j] + '":"' + str(rows[i][j]) + '"'

				j += 1

			rowOutput += properties + '}'
			rowOutput += '}'

			output += rowOutput

		# start over
		rowOutput = ""
		i += 1

	# Assemble the GeoJSON
	totalOutput = '{ "type": "FeatureCollection", "features": [ ' + output + ' ]}'

	# Write it to a file
	with open(arguments.file + '.geojson', 'w') as outfile:
		outfile.write(totalOutput)

	# If a TopoJSON conversion is requested...
	if arguments.topojson is True:
		topojson()
	else:
		print "Done!"

def topojson():
	command = "topojson -o " + arguments.file + ".topojson -p -- " + arguments.file + ".geojson" 
	subprocess.call(command, shell=True)

# Start the process
getData()
