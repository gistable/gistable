class Transaction(object):

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self.db.session

    def __exit__(self, type, value, traceback):
        if not value:
            self.db.session.commit()

# ...now we can do this:

with Transaction(db) as session:
    admin = User('admin', 'admin@example.com')
    session.add(admin) # session is available for adding etc.
    # automatic commit performed when exiting 'with' section

with Transaction(db):
    admin.email = 'root@example.com'
    # automatic commit performed when exiting 'with' section


# Apparently, this is reinventing the wheel, you can do almost the same with pure SQLAlchemy,
# see http://docs.sqlalchemy.org/en/latest/orm/session.html#autocommit-mode, following should
# work (not tested):

with db.session.begin():
    admin = User('admin')
    db.session.add(admin)
