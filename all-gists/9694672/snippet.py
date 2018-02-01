#!/usr/bin/python
import csv
import sys
import argparse
from string import Template
import subprocess

debug = False

def output(hdfspath,data):
	subprocess.call(['hdfs','dfs','-rm',hdfspath],shell=False)
	p = subprocess.Popen(['hdfs','dfs','-put','-',hdfspath],stdin=subprocess.PIPE)
	p.communicate(input=data)
	if (p.returncode!=0):
		error("failed to write %s"%hdfspath)
		exit(1)

def debug(str):
	if debug==True:
		print str

def error(str):
	print str


def genAvroSchema(coldict):

	ss = """
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
	%s
 ]
}""" % ",\n".join(['{"name": "%s", "type": "string"}' % x for x in coldict])
	debug(ss)
	output(args.schemafile,ss)

def genCSVDDL(coldict):
	cols = ",\n".join(['%s STRING' % x for x in coldict])
	ddl = """
		ADD JAR ${JSON_SERDE};
		drop table staging.%s_csv;
		CREATE EXTERNAL TABLE staging.%s_csv
		(%s)
		row format serde 'com.bizo.hive.serde.csv.CSVSerde'
		LOCATION '%s';
		""" % (args.tablename,args.tablename,cols,args.hdfsCSVDir)
	debug(ddl)
	output(args.csvDDL,ddl)

def genMergeDDL(coldict):
	cols = ",\n".join(['%s STRING' % x for x in coldict])
	sel_join_cols = ", \n".join(['gt.%s' % x for x in coldict])
	sel_cols = ", \n".join(['%s' % x for x in coldict])
	joincond =  " and ".join(['st.%s = gt.%s ' % (x,x) for x in args.primarykeys.split(',')])
	filter = " and ".join([' st.%s is null ' % x for x in args.primarykeys.split(',')])

	ddl = """
		ADD JAR ${JSON_SERDE};

		drop table staging.%s_merged;

		CREATE external TABLE staging.%s_merged
		(%s)
		ROW FORMAT SERDE
		'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
  		STORED AS INPUTFORMAT
  		'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat'
  		OUTPUTFORMAT
  		'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat'
		LOCATION '%s'
  		TBLPROPERTIES (
    		'avro.schema.url'='%s');

		insert overwrite table staging.%s_merged
		select * from (
		select %s
		from %s.%s gt
		left outer join staging.%s_csv st
		on %s
		where %s
		union all
		select %s
		from staging.%s_csv) T;

		use %s;

		alter table %s set location '%s';

		drop table staging.%s_merged;

		""" % (args.tablename,args.tablename,cols,args.hdfsTableDir,args.schemafile,
			args.tablename,sel_join_cols,args.dbname,args.tablename,args.tablename, joincond,filter,sel_cols,args.tablename,
			args.dbname,args.tablename,args.hdfsTableDir,args.tablename)
	debug(ddl)
	output(args.avroDDL,ddl)


csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser(fromfile_prefix_chars='@',description='Generate Avro schema and DDLs from CSV headers')
parser.add_argument('--filename',help='Path to CSV file',required=True);
parser.add_argument('--tablename',help='Base name of Hive table',default='mytable')
parser.add_argument('--dbname',help='Database where Hive tables will be located',default='default')
parser.add_argument('--schemafile',help='Path to output avro schema file',default='schema.avsc')
parser.add_argument('--csvDDL',help='Path to output with DDL for external CSV table',default='csv_table.hql')
parser.add_argument('--avroDDL',help='Path to output with DDL for Avro table',default='avro_table.hql')
parser.add_argument('--hdfsCSVDir',help='Location of CSV file in HDFS',default='~/mytable')
parser.add_argument('--hdfsTableDir',help='Location of real table file in HDFS',default='~/mytable')
parser.add_argument('--primarykeys',help='comman seperated lists of columns in primary key of table',default='id')


args = parser.parse_args();

#f =  file(args.filename,'r')
f = subprocess.Popen(['hdfs','dfs','-cat',args.filename],stdout=subprocess.PIPE)
stdout,stderr = f.communicate()
if f.returncode!=0:
	error("failed to read %s"%args.filename)
	exit(1)

debug(stdout)

reader = csv.DictReader(stdout.decode('ascii').splitlines())
debug(reader.fieldnames)
clean_names = [x.replace('/','_') for x in reader.fieldnames]
genAvroSchema(clean_names)
genCSVDDL(clean_names)
genMergeDDL(clean_names)