
import luigi
import tempfile
import datetime
from luigi.contrib import rdbms
from lib.luigi import logger
from luigi.postgres import MultiReplacer

try:
    import MySQLdb
    import MySQLdb.constants.ER as errorcode
except ImportError as e:
    logger.warning("Loading MySQL module without the python package MySQLdb. \
        This will crash at runtime if MySQL functionality is used.")


# these are the escape sequences recognized by mysql COPY
# according to http://www.postgresql.org/docs/8.1/static/sql-copy.html
default_escape = MultiReplacer([('\\', '\\\\'),
                                ('\0', '\\0'),
                                ('\'', '\\\''),
                                ('\"', '\\"'),
                                ('\b', '\\b'),
                                ('\n', '\\n'),
                                ('\r', '\\r'),
                                ('\t', '\\t'),
                                ])


class MySqlTarget(luigi.Target):
    """Target for a resource in MySql"""

    marker_table = luigi.configuration.get_config().get(
        'mysql', 'marker-table', 'table_updates')

    def __init__(self, host, database, user, password, table, update_id):
        """
        Args:
            host (str): MySql server address. Possibly a host:port string.
            database (str): Database name
            user (str): Database user
            password (str): Password for specified user
            update_id (str): An identifier for this data set

        """
        if ':' in host:
            self.host, self.port = host.split(':')
            self.port = int(self.port)
        else:
            self.host = host
            self.port = 3306
        self.database = database
        self.user = user
        self.password = password
        self.table = table
        self.update_id = update_id

    def touch(self, connection=None):
        """Mark this update as complete.

        Important: If the marker table doesn't exist, the connection
        transaction will be aborted and the connection reset. Then the marker
        table will be created.
        """
        self.create_marker_table()

        if connection is None:
            connection = self.connect()
            # if connection created here, we commit it here
            connection.autocommit(True)

        connection.cursor().execute(
            """INSERT INTO {marker_table} (update_id, target_table)
               VALUES (%s, %s)
            """.format(marker_table=self.marker_table),
            (self.update_id, self.table)
        )
        # make sure update is properly marked
        assert self.exists(connection)

    def exists(self, connection=None):
        if connection is None:
            connection = self.connect()
            connection.autocommit(True)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT 1 FROM {marker_table}
                WHERE update_id = %s
                LIMIT 1""".format(marker_table=self.marker_table),
                (self.update_id,)
            )
            row = cursor.fetchone()
        except MySQLdb.ProgrammingError as e:
            if e[0] == errorcode.NO_SUCH_TABLE:
                row = None
            else:
                raise
        return row is not None

    def connect(self, autocommit=False, local_infile=True):
        connection = MySQLdb.connect(user=self.user,
                                     passwd=self.password,
                                     host=self.host,
                                     port=self.port,
                                     db=self.database,
                                     local_infile=local_infile)
        connection.autocommit(autocommit)
        return connection

    def create_marker_table(self):
        """Create marker table if it doesn't exist.

        Using a separate connection since the transaction might have to be
        reset.
        """
        connection = self.connect(autocommit=True)
        cursor = connection.cursor()
        try:
            cursor.execute(
                """ CREATE TABLE {marker_table} (
                        id            BIGINT(20)    NOT NULL AUTO_INCREMENT,
                        update_id     VARCHAR(128)  NOT NULL,
                        target_table  VARCHAR(128),
                        inserted      TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (update_id),
                        KEY id (id)
                    )
                """
                .format(marker_table=self.marker_table)
            )
        except MySQLdb.OperationalError as e:
            if e[0] == errorcode.TABLE_EXISTS_ERROR:
                pass
            else:
                raise
        connection.close()


class CopyToTable(rdbms.CopyToTable):

    def rows(self):
        """Return/yield tuples or lists corresponding to each row to be
        inserted """
        with self.input().open('r') as fobj:
            for line in fobj:
                yield line.strip('\n').split(self.column_separator)

    def map_column(self, value):
        """Applied to each column of every row returned by `rows`

        Default behaviour is to escape special characters and identify any
        self.null_values
        """
        if value in self.null_values:
            return 'NULL'
        elif isinstance(value, unicode):
            return default_escape(value).encode('utf8')
        else:
            return default_escape(str(value))

    def output(self):
        return MySqlTarget(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            table=self.table,
            update_id=self.update_id(),
        )

    def copy_from(self, cursor, file_path, table, column_sep='\t',
                  row_sep='\n'):
        cursor.execute("""
        load data local infile '{file_path}' into table {table_name}
        columns terminated by '{column_sep}' lines terminated by '{row_sep}'
        """.format(file_path=file_path, table_name=table,
                   column_sep=column_sep, row_sep=row_sep))

    def copy(self, cursor, file):
        self.copy_from(cursor, file.name, self.table)

    def run(self):
        """Inserts data generated by rows() into target table.

        If the target table doesn't exist, self.create_table will be called to
        attempt to create the table.

        Normally you don't want to override this.
        """
        if not (self.table and self.columns):
            raise Exception("table and columns need to be specified")

        connection = self.output().connect()
        tmp_dir = luigi.configuration.get_config().get(
            'mysql', 'local-tmp-dir', None)
        tmp_file = tempfile.NamedTemporaryFile(dir=tmp_dir)
        n = 0
        for row in self.rows():
            n += 1
            if n % 100000 == 0:
                logger.info("Wrote %d lines", n)
            rowstr = '\t'.join(
                self.map_column(val) for val in row)
            tmp_file.write(rowstr + '\n')

        logger.info("Done writing, importing at %s", datetime.datetime.now())
        tmp_file.seek(0)

        # attempt to copy the data into mysql
        # if it fails because the target table doesn't exist
        # try to create it by running self.create_table
        for attempt in xrange(2):
            try:
                cursor = connection.cursor()
                self.init_copy(connection)
                self.copy(cursor, tmp_file)
            except MySQLdb.ProgrammingError, e:
                if e[0] == errorcode.NO_SUCH_TABLE and \
                        attempt == 0:
                    # if first attempt fails with "relation not found", try
                    # creating table
                    logger.info("Creating table %s", self.table)
                    connection.rollback()
                    self.create_table(connection)
                else:
                    raise
            else:
                break

        # mark as complete in same transaction
        self.output().touch(connection)

        # commit and clean up
        connection.commit()
        connection.close()
        tmp_file.close()