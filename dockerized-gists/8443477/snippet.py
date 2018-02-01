from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# a model
class Thing(Base):
    __tablename__ = 'thing'

    id = Column(Integer, primary_key=True)

# a database w a schema
engine = create_engine("postgresql://scott:tiger@localhost/test", echo=True)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


from unittest import TestCase
import unittest
from sqlalchemy.orm import Session
from sqlalchemy import event

class MyTests(TestCase):

    def setUp(self):
        # same setup from the docs
        self.conn = engine.connect()
        self.trans = self.conn.begin()
        self.session = Session(bind=self.conn)

        # load fixture data within the scope of the transaction
        self._fixture()

        # start the session in a SAVEPOINT...
        self.session.begin_nested()

        # then each time that SAVEPOINT ends, reopen it
        @event.listens_for(self.session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()

    def tearDown(self):
        # same teardown from the docs
        self.session.close()
        self.trans.rollback()
        self.conn.close()

    def _fixture(self):
        self.session.add_all([
            Thing(), Thing(), Thing()
        ])
        self.session.commit()

    def test_thing_one(self):
        # run zero rollbacks
        self._test_thing(0)

    def test_thing_two(self):
        # run two extra rollbacks
        self._test_thing(2)

    def test_thing_five(self):
        # run five extra rollbacks
        self._test_thing(5)

    def _test_thing(self, extra_rollback=0):
        session = self.session

        rows = session.query(Thing).all()
        self.assertEquals(len(rows), 3)

        for elem in range(extra_rollback):
            # run N number of rollbacks
            session.add_all([Thing(), Thing(), Thing()])
            rows = session.query(Thing).all()
            self.assertEquals(len(rows), 6)

            session.rollback()

        # after rollbacks, still @ 3 rows
        rows = session.query(Thing).all()
        self.assertEquals(len(rows), 3)

        session.add_all([Thing(), Thing()])
        session.commit()

        rows = session.query(Thing).all()
        self.assertEquals(len(rows), 5)

        session.add(Thing())
        rows = session.query(Thing).all()
        self.assertEquals(len(rows), 6)

        for elem in range(extra_rollback):
            # run N number of rollbacks
            session.add_all([Thing(), Thing(), Thing()])
            rows = session.query(Thing).all()
            if elem > 0:
                # b.c. we rolled back that other "thing" too
                self.assertEquals(len(rows), 8)
            else:
                self.assertEquals(len(rows), 9)
            session.rollback()

        rows = session.query(Thing).all()
        if extra_rollback:
            self.assertEquals(len(rows), 5)
        else:
            self.assertEquals(len(rows), 6)



if __name__ == '__main__':
    unittest.main()


