"""Here's how you implement Foo(pkid) with postgres.orm 2.1.x.

Discovered at PyTennesse with @wlphoenix @PederSchacht et al.

"""

class Foo(Model):
    typname = 'foo'

    def __new__(cls, pkid_or_record):
        if type(pkid_or_record) is int:
            obj = cls.db.one( 'select foo.*::foo from foo where pkid=%s'
                            , (pkid_or_record,)
                             )
            return obj
        else:
            return super().__new__(cls) # This is the Python 3 version of super.

    def __init__(self, record):
        if type(record) is dict:
            Model.__init__(self, record)