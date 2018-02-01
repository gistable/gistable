"""Print SQLAlchemy queries (including bind params)."""


def show_query(query):
    from sqlalchemy.dialects.postgresql import dialect
    qc = query.statement.compile(dialect=dialect())
    return str(query) % {n: repr(b.value) for n, b in qc.binds.items()}


def print_query(query):
    print(show_query(query))
