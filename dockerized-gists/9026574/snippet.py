import psycopg2 as pg
import pandas.io.sql as psql
 
# get connected to the database
connection = pg.connect("dbname=mydatabase user=postgres")
 
dataframe = psql.frame_query("SELECT * FROM <tablename>", connection)