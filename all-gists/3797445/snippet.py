#!/usr/bin/env python
"""An example of cursor dealing with prepared statements.

A cursor can be used as a regular one, but has also a prepare() statement. If
prepare() is called, execute() and executemany() can be used without query: in
this case the parameters are passed to the prepared statement. The functions
also execute the prepared statement if the query is the same prepared before.

Prepared statements aren't automatically deallocated when the cursor is
deleted, but are when the cursor is closed. For long-running sessions creating
an unbound number of cursors you should make sure to deallocate the prepared
statements (calling close() or deallocate() on the cursor).

"""

# Copyright (C) 2012 Daniele Varrazzo  <daniele.varrazzo@gmail.com>

import os
import re
from threading import Lock

import psycopg2
import psycopg2.extensions as ext

class PreparingCursor(ext.cursor):
    _lock = Lock()
    _ncur = 0
    def __init__(self, *args, **kwargs):
        super(PreparingCursor, self).__init__(*args, **kwargs)
        # create a distinct name for the statements prepared by this cursor
        self._lock.acquire()
        self._prepname = "psyco_%x" % self._ncur
        PreparingCursor._ncur += 1
        self._lock.release()

        self._prepared = None
        self._execstmt = None

    _re_replargs = re.compile(r'(%s)|(%\([^)]+\)s)')

    def prepare(self, stmt):
        """Prepare a query for execution.

        TODO: handle literal %s and $s in the string.
        """
        # replace the python placeholders with postgres placeholders
        parlist = []
        parmap = {}
        parord = []

        def repl(m):
            par = m.group(1)
            if par is not None:
                parlist.append(par)
                return "$%d" % len(parlist)
            else:
                par = m.group(2)
                assert par
                idx = parmap.get(par)
                if idx is None:
                    idx = parmap[par] = "$%d" % (len(parmap) + 1)
                    parord.append(par)

                return idx

        pgstmt = self._re_replargs.sub(repl, stmt)

        if parlist and parmap:
            raise psycopg2.ProgrammingError(
                "you can't mix positional and named placeholders")

        self.deallocate()
        self.execute("prepare %s as %s" % (self._prepname, pgstmt))

        if parlist:
            self._execstmt = "execute %s (%s)" % (
                self._prepname, ','.join(parlist))
        elif parmap:
            self._execstmt = "execute %s (%s)" % (
                self._prepname, ','.join(parord))
        else:
            self._execstmt = "execute %s" % (self._prepname)

        self._prepared = stmt

    @property
    def prepared(self):
        """The query currently prepared."""
        return self._prepared

    def deallocate(self):
        """Deallocate the currently prepared statement."""
        if self._prepared is not None:
            self.execute("deallocate " + self._prepname)
            self._prepared = None
            self._execstmt = None

    def execute(self, stmt=None, args=None):
        if stmt is None or stmt == self._prepared:
            stmt = self._execstmt
        elif not isinstance(stmt, basestring):
            args = stmt
            stmt = self._execstmt

        if stmt is None:
            raise psycopg2.ProgrammingError(
                "execute() with no query called without prepare")

        return super(PreparingCursor, self).execute(stmt, args)

    def executemany(self, stmt, args=None):
        if args is None:
            args = stmt
            stmt = self._execstmt

            if stmt is None:
                raise psycopg2.ProgrammingError(
                    "executemany() with no query called without prepare")
        else:
            if stmt != self._prepared:
                self.prepare(stmt)

        return super(PreparingCursor, self).executemany(self._execstmt, args)

    def close(self):
        if not self.closed and not self.connection.closed and self._prepared:
            self.deallocate()

        return super(PreparingCursor, self).close()



import unittest

class PreparingCursorTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(os.environ['TEST_DSN'])

    def tearDown(self):
        self.conn.close()

    def cursor(self):
        return self.conn.cursor(cursor_factory=PreparingCursor)

    def test_prepare_noargs(self):
        cur = self.cursor()
        self.assert_(not cur.prepared)
        cur.prepare("select 1")
        self.assertEqual(cur.prepared, "select 1")
        cur.execute()
        self.assertEqual(cur.fetchone(), (1,))

    def test_deallocate(self):
        cur = self.cursor()
        cur.execute("select * from pg_prepared_statements where name = %s",
            (cur._prepname,))
        self.assert_(not cur.fetchone())

        cur.prepare("select 1")
        self.assert_(cur.prepared)
        cur.execute("select * from pg_prepared_statements where name = %s",
            (cur._prepname,))
        self.assert_(cur.fetchone())

        cur.deallocate()
        self.assert_(not cur.prepared)
        cur.execute("select * from pg_prepared_statements where name = %s",
            (cur._prepname,))
        self.assert_(not cur.fetchone())

    def test_prepare_posargs(self):
        cur = self.cursor()
        cur.prepare("select 1 + %s::integer, %s::text")
        cur.execute((1,'foo'))
        self.assertEqual(cur.fetchone(), (2, 'foo'))
        cur.execute(None, [2,'bar'])
        self.assertEqual(cur.fetchone(), (3, 'bar'))

    def test_prepare_kwargs(self):
        cur = self.cursor()
        cur.prepare(
            "select %(foo)s::integer, %(bar)s::integer, %(foo)s::integer")
        cur.execute({'foo': 10, 'bar': 20})
        self.assertEqual(cur.fetchone(), (10, 20, 10))
        cur.execute(None, {'foo': 10, 'bar': 20})
        self.assertEqual(cur.fetchone(), (10, 20, 10))

    def test_executemany(self):
        cur = self.cursor()
        cur.execute("create table testem(id int, data text)")
        cur.executemany("insert into testem values (%s, %s)",
            [(i, i) for i in range(10)])
        cur.execute("select min(id), max(data), count(*) from testem")
        self.assertEqual(cur.fetchone(), (0, "9", 10))

    def test_prepare_executemany(self):
        cur = self.cursor()
        cur.execute("create table testem(id int, data text)")
        cur.prepare("""
            insert into testem values
            (%(foo)s::integer, %(foo)s::text)""")
        cur.executemany([{'foo': i, 'bar': 2*i} for i in range(10)])
        cur.execute("select min(id), max(data), count(*) from testem")
        self.assertEqual(cur.fetchone(), (0, "9", 10))

    def test_nomix(self):
        cur = self.cursor()
        self.assertRaises(psycopg2.ProgrammingError,
            cur.prepare, "select 1 + %s::integer, %(foo)s::text")

    def test_many(self):
        cur1 = self.cursor()
        cur2 = self.cursor()
        cur1.prepare("select 1")
        cur2.prepare("select 2")
        cur1.execute()
        cur2.execute()
        self.assertEqual(cur1.fetchone(), (1,))
        self.assertEqual(cur2.fetchone(), (2,))

    def test_execute_prepared(self):
        cur = self.cursor()
        cur.prepare("select %s::integer")
        cur.execute("select %s::integer", (10,))
        self.assert_(cur.query.startswith("execute"))


if __name__ == '__main__':
    unittest.main()
