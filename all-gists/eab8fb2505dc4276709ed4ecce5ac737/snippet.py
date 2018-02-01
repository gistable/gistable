class SomeExport(luigi.Task):
    date = luigi.DateParameter(default=datetime.date.today())

    def output(self):
        return luigi.s3.S3Target(self.date.strftime('s3://mybucket/%Y%m%d.txt.gz'))

    def requires(self):
        return None

    def run(self):
        '''
        Extract query and Ship to S3 for ingestion.
        '''
        query = '''
                    select ... from ...
                '''

        with create_engine('mssql+pymssql://{}:{}@{}/{}'.format(user, passw, host, db)) as engine:
            conn = engine.connect()
            cursor = conn.execute(query)
            with gzip.open(self.date.strftime('somefile%Y%m%d.txt.gz'), 'wb') as outfile:
                writer = csv.DictWriter(outfile, delimiter=',', fieldnames=cursor.keys(), quoting=csv.QUOTE_ALL)
                writer.writeheader()
                data = cursor.fetchmany(10000)
                while data:
                    for row in data:
                        writer.writerow(row)
                    data = cursor.fetchmany(10000)

        s3 = boto3.resource('s3')
        s3file = s3.Object('mybucket', '{}'.format(self.date.strftime('somefile%Y%m%d.txt.gz')))
        s3file.put(Body=open(self.date.strftime('somefile%Y%m%d.txt.gz'), 'rb'))
        
class SomeDataLoad(redshift.S3CopyToTable):
    """Load file to redshift"""
    date = luigi.DateParameter(default=datetime.date.today())
    host = redshift_host
    database = redshift_db
    user = redshift_user
    password = redshift_pass
    aws_access_key_id = aws_key
    aws_secret_access_key = aws_secret
    table = 'myschema.mytable'
    copy_options = r"REGION 'us-east-1' CSV EMPTYASNULL IGNOREHEADER 1 GZIP"
    columns = [
                    ('col', 'type'),
                    ('col2', 'type')
                    ...
                ]

    def init_copy(self, connection):  # Optionally replace the existing data with the current data
            cur = connection.cursor()
            query = 'truncate myschema.mytable;'
            cur.execute(query)

    def s3_load_path(self):
        return self.date.strftime('s3://mybucket/somefile%Y%m%d.txt.gz')

    def post_copy(self, cursor):  # Optionally do some other arbitrary query on successful load of the data
            query = """
                    update myschema.mytable
                    ...;
                    """
            cursor.execute(query)

    def requires(self):
        return EnterpriseMembershipExtract(datetime.date.today())