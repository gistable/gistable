from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData, inspect

def relational_diagram(*args, **kwargs):
    Base = automap_base()
    engine = create_engine(*args, **kwargs)
    Base.prepare(engine, reflect=True)
    meta = MetaData()
    meta.reflect(bind=engine)
    insp = inspect(engine)
    result = ["%%mocodo"]
    for table_name in insp.get_table_names():
        foreign_keys = {}
        for data in insp.get_foreign_keys(table_name):
            for (column, key) in zip(data["constrained_columns"], data["referred_columns"]):
                foreign_keys[column] = "#%s->%s->%s" % (column, data["referred_table"], key)
        items = []
        for (i, column) in enumerate(insp.get_columns(table_name)):
            prefix = ("_" if i and column["primary_key"] else "")
            item = prefix + foreign_keys.get(column["name"], column["name"])
            items.append(item)
        result.append("%s: %s" % (table_name, ", ".join(items)))
    return "\n".join(result)