from sqlalchemy.dialects import postgresql
print(YOUR_SQL.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))