import psycopg2 as pg

from io import BytesIO
from collections import defaultdict
from contextlib import contextmanager
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED

READ_COMMIT = ISOLATION_LEVEL_READ_COMMITTED
AUTO_COMMIT = ISOLATION_LEVEL_AUTOCOMMIT

class SchemaCloner(object):

  def __init__(self, dsn = None, *args, **kwargs):
    self.__connection   = pg.connect(dsn) if dsn else pg.connect(*args, **kwargs)
    self.__cursor       = None
    self.__schemas      = None
    self.__schema       = 'public'

    self.__tables       = {}
    self.__columns      = {}
    self.__constraints  = {}
    self.__sequences    = {}
    self.__indexes      = {}
    self.__primary_keys = {}

    self.read_commit # ensure we're using transactions

  @property
  def _cursor(self):
    if not self.__cursor:
      self.__cursor = self.__connection.cursor()
    return self.__cursor

  @property
  def _connection(self):
    return self.__connection

  @property
  def isolation(self):
    return self._connection.isolation_level

  @property
  def auto_commit(self):
    self.isolation = AUTO_COMMIT
    return self.isolation

  @property
  def read_commit(self):
    self.isolation = READ_COMMIT
    return self.isolation

  @contextmanager
  def isolation_context(self, level):
    original_level = self.isolation
    try:
      self.isolation = level
      yield
    finally:
      self.isolation = original_level

  @isolation.setter
  def isolation(self, value):
    return self._connection.set_isolation_level(value)

  @property
  def schema(self):
    return self.__schema

  @schema.setter
  def schema(self, value):
    old_schema = self.__schema
    self.__schema = value
    return old_schema

  @property
  def schemas(self):
    if not self.__schemas:
      results = self.query("""
        SELECT n.oid AS schema_id, n.nspname AS schema_name, r.rolname AS owner
          FROM pg_namespace AS n
          JOIN pg_roles AS r ON n.nspowner = r.oid
        """)
      self.__schemas = dict( ( _name, ( _id, _owner )) for _id, _name, _owner in results )
    return self.__schemas

  @property
  def schema_oid(self):
    return self.schemas[self.schema][0]

  @property
  def schema_owner(self):
    return self.schemas[self.schema][1]

  @property
  def sequences(self):
    if not self.schema in self.__sequences:
      sequences = self.query("""
        SELECT quote_ident(S.relname) AS sequence_name,
               quote_ident(T.relname) AS table_name,
               quote_ident(C.attname) AS column_name
        FROM pg_class AS S,
             pg_depend AS D,
             pg_class AS T,
             pg_attribute AS C,
             pg_tables AS PGT
        WHERE S.relkind = 'S'
            AND S.oid = D.objid
            AND D.refobjid = T.oid
            AND D.refobjid = C.attrelid
            AND D.refobjsubid = C.attnum
            AND T.relname = PGT.tablename
            AND PGT.schemaname = %s
        ORDER BY sequence_name;
        """, (self.schema,))
      tables = defaultdict(
        lambda: {},
        dict((seq, {tbl: col}) for seq, tbl, col in set(sequences))
      )
      self.__sequences[self.schema] = tables
    return self.__sequences[self.schema]

  @property
  def tables(self):
    if not self.schema in self.__tables:
      results = self.query("""
        SELECT relfilenode, relname
          FROM pg_class
         WHERE relnamespace = %s AND relkind = %s
        """, (self.schema_oid,'r',))
      self.__tables[self.schema] = dict( ( _name, _id ) for _id, _name in results )
    return self.__tables[self.schema]

  @property
  def primary_keys(self):
    if not self.schema in self.__primary_keys:
      # if primaries haven't yet been loaded, get them all
      primaries = self.query("""
        SELECT pgct.relname AS table_name,
               con.conname AS constraint_name,
               pg_catalog.pg_get_constraintdef(con.oid) AS constraint_definition
          FROM pg_catalog.pg_constraint AS con
          JOIN pg_class AS pgct ON pgct.relnamespace = con.connamespace AND pgct.oid = con.conrelid
         WHERE pgct.relnamespace = %s AND con.contype = %s;
        """, (self.schema_oid, 'p', ))

      tables = {}
      for table in set( [ p[0] for p in primaries ] ):
        tables[table] = map(lambda p: (p[1], p[2]), filter(lambda p: p[0] == table, primaries))
      self.__primary_keys[self.schema] = defaultdict(lambda: [], tables)
    return self.__primary_keys[self.schema]

  @property
  def indexes(self):
    if not self.schema in self.__indexes:
      self.__indexes[self.schema] = {}

      indexes = self.query("""
        SELECT pgct.relname AS table_name,
               pg_catalog.pg_get_indexdef(pgi.indexrelid) AS index_definition
          FROM pg_index pgi
          JOIN pg_class AS pgci ON pgci.oid = pgi.indexrelid
          JOIN pg_class AS pgct ON pgct.oid = pgi.indrelid
         WHERE pgci.relnamespace = %s AND pgi.indisprimary = false
        """, (self.schema_oid,) )

      tables = {}
      for table in set( [ i[0] for i in indexes ] ):
        tables[table] = map(lambda i: i[1], filter(lambda i: i[0] == table, indexes))
      self.__indexes[self.schema] = defaultdict(lambda: [], tables)
    return self.__indexes[self.schema]

  @property
  def columns(self):
    if not self.schema in self.__columns:
      self.__columns[self.schema] = {}

      columns = self.query("""
        SELECT table_name, column_name, column_default
          FROM information_schema.columns
         WHERE table_schema = %s
        """, (self.schema,))

      tables = {}
      for table in set( [ c[0] for c in columns ] ):
        tables[table] = map(lambda c: (c[1], c[2]), filter(lambda c: c[0] == table, columns))
      self.__columns[self.schema] = defaultdict(lambda: [], tables)
    return self.__columns[self.schema]

  @property
  def constraints(self):
    if not self.schema in self.__constraints:
      # if constraints haven't yet been loaded, get them all
      constraints = self.query("""
        SELECT pgct.relname AS table_name,
               con.conname AS constraint_name,
               pg_catalog.pg_get_constraintdef(con.oid) AS constraint_definition
          FROM pg_catalog.pg_constraint AS con
          JOIN pg_class AS pgct ON pgct.relnamespace = con.connamespace AND pgct.oid = con.conrelid
         WHERE pgct.relnamespace = %s AND con.contype = %s;
        """, (self.schema_oid, 'f', ))

      tables = {}
      for table in set( [ con[0] for con in constraints ] ):
        tables[table] = map(lambda c: (c[1], c[2]), filter(lambda c: c[0] == table, constraints))
      self.__constraints[self.schema] = defaultdict(lambda: [], tables)
    return self.__constraints[self.schema]

  def query_one(self, sql, *args, **kwargs):
    self._cursor.execute(sql, *args, **kwargs)
    return self._cursor.fetchone()

  def query(self, sql, *args, **kwargs):
    try:
      self.execute(sql, *args, **kwargs)
      return self._cursor.fetchall()
    except Exception, e:
      print "Exception during query: ", e
      print "   sql   : ", sql
      print "   args  : ", args
      print "   kwargs: ", kwargs
      raise e

  def execute(self, sql, *args, **kwargs):
    print self._cursor.mogrify(sql, *args, **kwargs)
    self._cursor.execute(sql, *args, **kwargs)

  def commit(self):
    self._connection.commit()

  def rollback(self):
    self._connection.rollback()

  def clone(self, source, destination):
    with self.isolation_context(READ_COMMIT):
      self.schema    = source
      self.isolation = ISOLATION_LEVEL_READ_COMMITTED

      # create schema
      self.execute('CREATE SCHEMA %s' % destination)
      self.execute('ALTER SCHEMA %s OWNER TO "%s"' % (destination, self.schema_owner))
      self.execute('SET search_path = %s, pg_catalog' % destination)

      # create sequences
      for sequence in self.sequences.keys():
        self.execute("CREATE SEQUENCE %s.%s" % (destination, sequence, ))

      # first table pass - create tables, sequences, defaults and ownerships
      for table in self.tables.keys():
        self.execute('CREATE TABLE %s.%s (LIKE %s.%s INCLUDING DEFAULTS)' % (destination, table, source, table,))
        self.execute('ALTER TABLE %s.%s OWNER TO "%s"' % (destination, table, self.schema_owner,))

        # update sequences to use destination schema sequence instead of source
        columns = filter(lambda col: col[1] and col[1].startswith('nextval'), self.columns[table])
        for column, default_value in columns:
          default_value  = default_value.replace('%s.' % source, '%s.' % destination)
          sequence_table = default_value.split("'")[1]
          self.execute('ALTER SEQUENCE %s OWNED BY %s.%s' % (sequence_table, table, column,))
          self.execute('ALTER TABLE ONLY %s ALTER COLUMN %s SET DEFAULT %s' % (table, column, default_value,))

      # second table pass - copy data
      for table in self.tables.keys():
        data = BytesIO()
        self._cursor.copy_to(data, "%s.%s" % (source, table), sep="|")
        data.seek(0)
        self._cursor.copy_from(data, "%s.%s" % (destination, table), sep="|")
        print "Copied %d bytes from %s.%s -> %s.%s" % (data.seek(0, 2), source, table, destination, table)


      # third pass - create primary keys and indexes
      for table in self.tables.keys():
        for key_name, key_definition in self.primary_keys[table]:
          key_definition = key_definition.replace('%s.' % source, '%s.' % destination)
          self.execute('ALTER TABLE ONLY %s ADD CONSTRAINT %s %s' % (table, key_name, key_definition))
        for index_definition in self.indexes[table]:
          index_definition = index_definition.replace('%s.' % source, '%s.' % destination)
          self.execute(index_definition)

      # fourth pass - create constraints
      for table in self.tables.keys():
        for constraint_name, constraint_definition in self.constraints[table]:
          constraint_definition = constraint_definition.replace('%s.' % source, '%s.' % destination)
          self.execute('ALTER TABLE ONLY %s ADD CONSTRAINT %s %s' % (table, constraint_name, constraint_definition))

      # fifth pass - fix sequences. Inserting as part of copy_from doesn't update the sequences, so we do that here.
      for sequence in self.sequences.keys():
        for table, column in self.sequences[sequence].items():
          self.execute("""
            SELECT setval('%s', (SELECT COALESCE(MAX(%s), 1) FROM %s), true)
            """.strip() % (sequence, column, table))

      # and we're done...
      self.commit()
