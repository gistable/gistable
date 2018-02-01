from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool, MetaData, Table, ForeignKeyConstraint
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from flask import current_app
config.set_main_option('sqlalchemy.url', current_app.config.get('SQLALCHEMY_DATABASE_URI'))
prototype_schema = current_app.config['PROTOTYPE_SCHEMA'] # base migrations on this schema
public_schema_tables = current_app.config['PUBLIC_SCHEMA_TABLES'] # table names that belong in 'public', not tenant schemas
get_schemas_query = current_app.config['GET_SCHEMAS_QUERY'] # query that returns a list of tenant schemas

def include_schemas(names):
    # produce an include object function that filters on the given schemas
    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "table":
            return object.schema in names
        return True
    return include_object

def lookup_correct_schema(name):
    if name in public_schema_tables:
        return 'public'
    else:
        return prototype_schema

def _get_table_key(name, schema):
    if schema is None:
        return name
    else:
        return schema + "." + name

def tometadata(table, metadata, schema):
    key = _get_table_key(table.name, schema)
    if key in metadata.tables:
        return metadata.tables[key]

    args = []
    for c in table.columns:
        args.append(c.copy(schema=schema))
    new_table = Table(
        table.name, metadata, schema=schema,
        *args, **table.kwargs
        )
    for c in table.constraints:
        if isinstance(c, ForeignKeyConstraint):
            constraint_schema = lookup_correct_schema(c.elements[0].column.table.name)
        else:
            constraint_schema = schema
        new_table.append_constraint(c.copy(schema=constraint_schema, target_table=new_table))

    for index in table.indexes:
        # skip indexes that would be generated
        # by the 'index' flag on Column
        if len(index.columns) == 1 and \
                list(index.columns)[0].index:
            continue
        Index(index.name,
              unique=index.unique,
              *[new_table.c[col] for col in index.columns.keys()],
              **index.kwargs)
    return table._schema_item_copy(new_table)

meta = current_app.extensions['migrate'].db.metadata
meta_schemax = MetaData()
for table in meta.tables.values():
    tometadata(table, meta_schemax, lookup_correct_schema(table.name))
target_metadata = meta_schemax

# target_metadata = current_app.extensions['migrate'].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = engine_from_config(
                config.get_section(config.config_ini_section),
                prefix='sqlalchemy.',
                poolclass=pool.NullPool)

    schemas = set([prototype_schema,None])

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True, #schemas,
        include_object=include_schemas([None,prototype_schema])
    )

    try:
        # get the schema names
        tenant_schemas = [row[0] for row in connection.execute(get_schemas_query)]
        for schema in tenant_schemas:
            connection.execute('set search_path to "{}", public'.format(schema))
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    print "Can't run migrations offline"
    # run_migrations_offline()
else:
    run_migrations_online()

