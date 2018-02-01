#! /usr/bin/pythonw
#
#	Modified by Michael Bianco <info@cliffsidedev.com> on June 26, 2009
#	Written by Thomas Pan at January 21, 2007
#	mysql2graffle for Omnigraffle 5 is based on
#	MyDBGraffle for OmniGraffle 4 which is based on Paul Davis' work at http://www.visualdistortion.org
#
#	Requires:
#
#		OmniGraffle 5
#			http://www.omnigroup.com/applications/omnigraffle/
#
#		Python
#			http://www.python.org
#
#		AppScript
#			http://freespace.virgin.net/hamish.sanderson/appscript.html
#			sudo easy_install appscript
#			sudo easy_install MySQL-python
#
#		MySQL 5
#			http://www.mysql.com
#
#	Warranty and liability:
#       THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED 
#       BY APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE 
#       COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS 
#       IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, 
#       INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
#       MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE 
#       RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. 
#       SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL 
#       NECESSARY SERVICING, REPAIR OR CORRECTION. YOU ARE LIABLE FOR 
#       DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL 
#       DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM 
#       (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED 
#       INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A 
#       FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS)
#

# TODO use ScriptingBridge instead of appscript
# TODO deal with constraint overlapping
# TODO deal with multiple column foreign key
# TODO deal with unique indexes
# TODO order columns based on names?

import sys
import re
from appscript import *
# from pg import DB
import _mysql
import string

####################################################
#  Some default settings for OmniGraffle Graphics  #
####################################################

# Common to title and all types of columns.
common_props = {}
common_props[ k.shadow_vector ]			= [ 7.0, 7.0 ]
common_props[ k.shadow_fuzziness ]		= 17.45
common_props[ k.autosizing ]			= k.full
common_props[ k.text_placement ]		= k.top
common_props[ k.draws_stroke ]			= False
common_props[ k.fill ]					= k.linear_fill
common_props[ k.fill_color ]			= [ 1, 1, 1 ]
common_props[ k.gradient_center ]		= [ 0.5, 0 ]
common_props[ k.magnets ]				= [ [ 1, 0 ], [ -1, 0 ] ]
#common_props[ k.size ]					= [ 90, 14 ]

#Table Name
table_name = common_props.copy()
table_name[ k.gradient_color ]			= [ 0, 0, 1 ]

#Primary Keys
column_pkey = common_props.copy()
column_pkey[ k.gradient_color ]			= [ 1, 0, 0 ]

#Foreign Keys
column_fkey = common_props.copy()
column_fkey[ k.gradient_color ]			= [ 0, 1, 0 ]

#No Key
column_norm = common_props.copy()
column_norm[ k.gradient_color ]			= [ 1, 1, 1 ]

#Line Properties
line_props = {}
line_props[ k.line_type ]				= k.orthogonal
line_props[ k.head_type ]				= "FilledArrow"
line_props[ k.jump ]					= True

###########################################
#  The query used to gather schema data.  #
###########################################

query = """
select  c.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable,
                tc.constraint_type,
                kcu.referenced_table_name,
                kcu.referenced_column_name,
                tc.constraint_name
from    information_schema.columns as c
                left join
                        information_schema.key_column_usage as kcu
                        on (
                                c.column_name = kcu.column_name
                                and c.table_schema = kcu.table_schema
                                and c.table_name = kcu.table_name
                        )
                left join
                        information_schema.table_constraints as tc
                        on (
                                        tc.constraint_name = kcu.constraint_name
                                and tc.table_schema = kcu.table_schema
                                and tc.table_name = kcu.table_name
                        )
where   c.table_schema = 'SCHEMA_NAME'
group by
        c.table_name,
        c.column_name
order   by
                c.table_name,
                c.ordinal_position
"""

#########################
#  Method definitions.  #
#########################

def parseArguments():
	"""
		I haven't taken the time to learn getopt, so I use regular expressions.
	"""
	options[ 'graffle' ] = 'OmniGraffle 5'
	options[ 'dbhost' ] = 'localhost'
	options[ 'dbport' ] = 5432
	options[ 'dbuser' ] = ''
	options[ 'dbpass' ] = ''
	options[ 'dbname' ] = ''
	options[ 'schema' ] = 'public'
	
	for key in options:
		value = options[key]
		print "Enter %s (%s): " % (key, value)
		data = raw_input()
		if data: options[key] = data

	options[ 'query' ] = re.compile( 'SCHEMA_NAME' ).sub( options[ 'dbname' ].lower(), query )

#Get the information we need to draw from the database
def getSchemaInfo( options, sql_tables, sql_references ):
	"""
		Connect to the database and retrieve our schema information.
	"""
        conn = _mysql.connect(host=options[ 'dbhost' ], user=options[ 'dbuser' ], db=options[ 'dbname' ], passwd=options['dbpass'])
	conn.query( options[ 'query' ] )
        rows = conn.store_result()
        res = rows.fetch_row(0, 1)

	for i in range( len( res ) ):
		ftbl		= res[i][ 'table_name' ]
		fcol		= res[i][ 'column_name' ]
		type		= res[i][ 'data_type' ] 
		nullable	= res[i][ 'is_nullable' ]
		keytype		= res[i][ 'constraint_type' ]
		ttbl		= res[i][ 'referenced_table_name' ]
		tcol		= res[i][ 'referenced_column_name' ]

		if not sql_tables.has_key( ftbl ):
			sql_tables[ ftbl ] = []

		sql_tables[ ftbl ] += [ [ fcol, type, nullable, keytype ] ] 

		if keytype == 'FOREIGN KEY' :
			sql_references += [ [ ftbl, fcol, ttbl, tcol ] ]

#Create a table in OmniGraffle from database info
def createOGTableFromSQLTable( graffle, name, sql_table, og_tables ):
	"""
		Create a table in OmniGraffle using data from the database
	"""
	shapes = []
	graphics = graffle.windows[1].document.canvases[1].graphics 

	graphics.end.make( new=k.shape, with_properties=table_name )
	shape = graphics.last.get()
	shape.text.set( name )
	shapes += [ shape ]

	use_props = None
	for i in range( len( sql_table ) ):

		if sql_table[i][3] == 'PRIMARY KEY' :
			use_props = column_pkey
		elif sql_table[i][3] == 'FOREIGN KEY' :
			use_props = column_fkey
		else :
			use_props = column_norm

		graphics.end.make( new=k.shape, with_properties=use_props )
		shape = graphics.last.get()
		shape.text.set( sql_table[i][0] ) 
		shapes += [ shape ]

	og_tables[ name.upper() ] = graffle.assemble( shapes, table_shape=[len( sql_table)+1,1] )
	og_tables[ name.upper() ].slide( by={ k.x:25,k.y:25} )

#Get the source and destination graphics for a line to be drawn
def getOGGraphicsFromReference( sql_reference, og_tables ) :
	ftbl = og_tables[ sql_reference[0].upper() ]
	fg = None
	for col in ftbl.columns[1].graphics.get() :
		if( col.text.get() == sql_reference[1] ) :
			fg = col.get() ;
			break ;
	else:
		raise RuntimeError, "Failed to find graphic for " + sql_reference[0] + "( " + sql_reference[1] + " )"

	ttbl = og_tables[ sql_reference[2].upper() ]
	tg = None
	for col in ttbl.columns[1].graphics.get() :
		if( col.text.get() == sql_reference[3] ) :
			tg = col.get() ;
			break ;
	else:
		raise RuntimeError, "Failed to find graphic for " + sql_reference[2] + "( " + sql_reference[3] + " )"

	return [ fg, tg ]

#Draw a line representing a reference in the database.
def createOGLineFromReference( graffle, sql_reference, og_tables ) :
	tgs = getOGGraphicsFromReference( sql_reference, og_tables )
	tgs[0].connect( to=tgs[1], with_properties=line_props )

#####################
#  Run the script.  #
#####################

options = {}

sql_tables = {}
sql_references = []

og_tables = {}

parseArguments()
graffle = app( options[ 'graffle' ] )
getSchemaInfo( options, sql_tables, sql_references )

for key in sql_tables.keys() :
	createOGTableFromSQLTable( graffle, key, sql_tables[ key ], og_tables ) 

graffle.windows[1].document.canvases[1].layout_info.properties.set( { k.type:k.force_directed} )
graffle.windows[1].document.canvases[1].layout()

for i in range( len( sql_references ) ) :
	createOGLineFromReference( graffle, sql_references[ i ], og_tables )
