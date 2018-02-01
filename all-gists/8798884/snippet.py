def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count

q = session.query(TestModel).filter(...).order_by(...)

# Slow: SELECT COUNT(*) FROM (SELECT ... FROM TestModel WHERE ...) ...
print q.count()

# Fast: SELECT COUNT(*) FROM TestModel WHERE ...
print get_count(q)