import pandas as pd
import pymysql
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://<user>:<password>@<host>[:<port>]/<dbname>')

df = pd.read_sql_query('SELECT * FROM table', engine)
df.head()