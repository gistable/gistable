"""
Mirror of code here: http://dev.utek.pl/2013/ignoring-tables-in-alembic/

Usage:

[alembic:exclude]
tables = spatial_ref_sys
"""

def exclude_tables_from_config(config_):
    tables_ = config_.get("tables", None)
    if tables_ is not None:
        tables = tables_.split(",")
    return tables

exclude_tables = exclude_tables_from_config(config.get_section('alembic:exclude'))

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in exclude_tables:
        return False
    else:
        return True

def run_migrations_online():
    if isinstance(engine, Engine):
        connection = engine.connect()
    else:
        raise Exception('Expected engine instance got %s instead' % type(engine))

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()
