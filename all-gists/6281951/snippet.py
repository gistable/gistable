def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print 'Clear table %s' % table
        session.execute(table.delete())
    session.commit()