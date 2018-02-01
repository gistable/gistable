# see also https://github.com/wrobstory/pgshift

import gzip
from io import StringIO, BytesIO
from functools import wraps

import boto
from sqlalchemy import MetaData
from pandas import DataFrame
from pandas.io.sql import SQLTable, pandasSQL_builder
import psycopg2

def monkeypatch_method(cls):
    @wraps(cls)
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator

def resolve_qualname(table_name, schema=None):
    name = '.'.join([schema, table_name]) if schema is not None else table_name
    return name

def does_table_exist(engine, schema, qualname):
    md = MetaData(engine, schema=schema, reflect=True)
    return qualname in md.tables.keys()


@monkeypatch_method(DataFrame)
def to_redshift(self, table_name, engine, bucket, keypath=None,
                schema=None, if_exists='fail', index=True, index_label=None,
                aws_access_key_id=None, aws_secret_access_key=None,
                columns=None, null_as=None, emptyasnull=True):
    """
    Write a DataFrame to redshift via S3

    Parameters
    =========

    table_name : str. (unqualified) name in redshift
    engine : SQLA engine
    bucket : str; s3 bucket
    keypath : str; keypath in s3 (without bucket name)
    schema : redshift schema
    if_exits : str; {'fail', 'append', 'replace'}
    index : bool; include DataFrames index
    index_label : bool; label for the index
    aws_access_key_id / aws_secret_access_key : from ~/.boto by default
    columns : subset of columns to include
    null_as : treat these as null
    emptyasnull bool; whether '' is null
    """
    url = self.to_s3(keypath, engine, bucket=bucket, index=index,
                     index_label=index_label)
    qualname = resolve_qualname(table_name, schema)
    table = SQLTable(table_name, pandasSQL_builder(engine, schema=schema),
                     self, if_exists=if_exists, index=index)
    if columns is None:
        columns = ''
    else:
        columns = '()'.format(','.join(columns))
    print("Creating table {}".format(qualname))

    if table.exists():
        if if_exists == 'fail':
            raise ValueError("Table Exists")
        elif if_exists == 'append':
            queue = []
        elif if_exists == 'replace':
            queue = ['drop table {}'.format(qualname), table.sql_schema()]
        else:
            raise ValueError("Bad option for `if_exists`")

    else:
        queue = [table.sql_schema()]

    with engine.begin() as con:
        for stmt in queue:
            con.execute(stmt)

    s3conn = boto.connect_s3(aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key)

    conn = psycopg2.connect(database=engine.url.database,
                            user=engine.url.username,
                            password=engine.url.password,
                            host=engine.url.host,
                            port=engine.url.port,
                            sslmode='require')
    cur = conn.cursor()
    if null_as is not None:
        null_as = "NULL AS '{}'".format(null_as)
    else:
        null_as = ''

    if emptyasnull:
        emptyasnull = "EMPTYASNULL"
    else:
        emptyasnull = ''

    full_keypath = 's3://' + url

    print("COPYing")
    stmt = ("copy {qualname} {columns} from '{keypath}' "
            "credentials 'aws_access_key_id={key};aws_secret_access_key={secret}' "
            "GZIP "
            "{null_as} "
            "{emptyasnull}"
            "CSV;".format(qualname=qualname,
                          columns=columns,
                          keypath=full_keypath,
                          key=s3conn.aws_access_key_id,
                          secret=s3conn.aws_secret_access_key,
                          null_as=null_as,
                          emptyasnull=emptyasnull))
    cur.execute(stmt)
    conn.commit()
    conn.close()


@monkeypatch_method(DataFrame)
def to_s3(self, keypath, engine, bucket, index=True, index_label=None,
          compress=True, header=False):
    s3conn = boto.connect_s3()
    url = bucket + '/' + keypath
    bucket = s3conn.get_bucket(bucket)

    if compress:
        url += '.gz'
    key = bucket.new_key(url)

    fp, gzfp = StringIO(), BytesIO
    self.to_csv(fp, index=index, header=header)
    if compress:
        fp.seek(0)
        gzipped = gzip.GzipFile(fileobj=gzfp, mode='w')
        gzipped.write(bytes(fp.read(), 'utf-8'))
        gzipped.close()
        gzfp.seek(0)
    else:
        gzfp = fp
        gzfp.seek(0)
    print("Uploading")
    key.set_contents_from_file(gzfp)
    return url


