from sqlalchemy import exists, text, exc, select, and_, literal, cast
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement

class InsertFromSelect(Executable, ClauseElement):
    """ Insert from select"""

    def __init__(self, table, select, *fields, **kw):
        self.table = table
        self.select = select
        self.fields = fields

@compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kw):
    if element.fields:
        f = ' (%s) ' % ', '.join(element.fields)
    else:
        f = ' '
    return 'INSERT INTO %s%s(%s)' % (
        compiler.process(element.table, asfrom=True),
        f,
        compiler.process(element.select)
    )

class UpsertNode(Executable, ClauseElement):

    def __init__(self, update, insert):
        self.update = update
        self.insert = insert
        self._returning = None

@compiles(UpsertNode)
def visit_upsert_node(element, compiler, **kw):
    return 'WITH update as (%s) %s' % (
        compiler.process(element.update),
        compiler.process(element.insert)
        )

def upsert(table, **values):
    """ Upsert"""
    pks = table.primary_key.columns
    try:
        pks_pred = and_(*[c == values[c.key] for c in pks])
    except KeyError as e:
        raise exc.ArgumentError('missing pk for upsert: %s' % e)
    update = (table.update()
        .values(**values)
        .where(pks_pred)
        .returning(literal(1)))
    fields = [k for (k, v) in values.items()]
    vals = [cast(literal(v, table.c[k].type), table.c[k].type).label(k)
            for (k, v) in values.items()]
    insert = InsertFromSelect(
        table,
        select(vals).where('not exists (select 1 from update)'),
        *fields)

    return UpsertNode(update, insert)
