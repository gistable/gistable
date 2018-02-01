import sqlite3
import os
import argparse

try:
    import pyspark
    import pyspark.sql
except ImportError:
    import sys
    import os
    # TODO: unhardcode these
    os.environ["SPARK_HOME"] = '/opt/spark'
    sys.path.append('/opt/spark/python')
    sys.path.append('/opt/spark/python/lib/py4j-0.8.2.1-src.zip')
    import pyspark
    import pyspark.sql
    from pyspark.sql.types import *


# load spark stuff
conf = pyspark.SparkConf()
conf.set('spark.executor.memory', '4g')
conf.set('spark.sql.parquet.compression.codec', 'gzip')
#conf.set('spark.sql.parquet.compression.codec', 'snappy')
sc = pyspark.SparkContext("local", conf=conf)
sqlContext = pyspark.SQLContext(sc)


def get_table_list(sqldb_loc):
    """Gets the list of tables in the sqlite database given a file path
        to the sqlite database
    """
    conn = sqlite3.connect(sqldb_loc)
    cur = conn.cursor()
    res = cur.execute("""SELECT name
                           FROM sqlite_master
                           WHERE type='table'""")
    names = [x[0] for x in res]
    cur.close()
    return names


def get_generator_from_table(sqldb_loc, table_name):
    conn = sqlite3.connect(sqldb_loc)
    cur = conn.cursor()
    res = cur.execute("""
    SELECT * FROM {0}
    """.format(table_name))
    for row in  res:
        yield row
    cur.close()
    conn.close()

def get_column_names_from_table(sqldb_loc, table_name):
    conn = sqlite3.connect(sqldb_loc)
    cur = conn.cursor()
    res = cur.execute("""
    SELECT *
    FROM {0}
    """.format(table_name))
    names = [x[0] for x in cur.description]
    cur.close()
    conn.close()
    return names

def create_df_from_generator(gen, names):
    a = sc.parallelize(gen, 20)
    a.persist(pyspark.StorageLevel(True, True, False, True, 1))
    df = sqlContext.createDataFrame(a, schema=names, samplingRatio=None).repartition(20)
    #df.persist(pyspark.StorageLevel(True, True, False, True, 1))
    return df


def sqlite2parquet(db_path, output_dir, skip_tables=['sqlite_sequence']):
    tables = get_table_list(db_path)
    for table in tables:
        if table in skip_tables:
            print "Skipping: {0}".format(table)
            continue
        print "Converting: {0}".format(table)
        gen = get_generator_from_table(db_path, table)
        if table in schemas:
            print "\t known schema"
            schema = schemas[table]
        else:
            schema = get_column_names_from_table(db_path, table)
        print "\t converting to data-frame"
        df = create_df_from_generator(gen, schema)
        p = os.path.join(output_dir, table + '.parquet')
        print "\t saving..."
        df.saveAsParquetFile(p)

def main():
    parser = argparse.ArgumentParser(description='Convert sqlite database into parquet files')
    parser.add_argument('sqlite_db_path')
    args = parser.parse_args()
    try:
        os.makedirs(args.sqlite_db_path + '.parquets')
    except OSError:
        #mmm quiet failure... brilliant!
        pass
    sqlite2parquet(args.sqlite_db_path, args.sqlite_db_path + '.parquets', skip_tables=['task', 'sqlite_sequence', 'sqlite_stat1', 'crawl'])

if __name__ == "__main__":
    main()
