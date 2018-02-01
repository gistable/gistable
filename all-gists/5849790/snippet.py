# -*- coding: utf-8 -*-
"""
Performance test for different types of update



Results sample
-----------------------------------------------

In [1]: import db_test

In [2]: db_test.prepare()

In [3]: %timeit db_test.insert_on_duplicate_key_update()
10 loops, best of 3: 61 ms per loop

In [4]: db_test.prepare()

In [5]: %timeit db_test.update()
10 loops, best of 3: 52.1 ms per loop

In [6]: db_test.prepare()

In [7]: %timeit db_test.update_case()
10 loops, best of 3: 33.3 ms per loop

"""
import random
import MySQLdb

db = MySQLdb.connect(host='localhost', db='db_test', read_default_file='~/.my.cnf')
db.autocommit(False)

nrows = 100
nrows_total = 100000


def prepare():
    """
    Prepare mysql table "foo"
    """
    c = db.cursor()
    c.execute("""
    DROP TABLE IF EXISTS `foo`;
    CREATE TABLE `foo` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `rating` int(11) NOT NULL,
         PRIMARY KEY (`id`)
    ) ENGINE InnoDB DEFAULT CHARSET latin1;
    """)
    c.close()
    c = db.cursor()
    rating_values = [(1, ) for _ in xrange(nrows_total)]
    c.executemany("INSERT INTO `foo` (`rating`) VALUES (%s)", rating_values)
    c.close()
    db.commit()


def insert_on_duplicate_key_update():
    """
    Update multiple rows at once with "INSERT .. ON DUPLICATE" statement
    """
    ids = random.sample(xrange(1, nrows_total + 1), nrows)
    rating_values = [(id, 2) for id in ids]
    c = db.cursor()
    c.executemany('INSERT INTO `foo` (`id`, `rating`) VALUES (%s, %s) '
                  'ON DUPLICATE KEY UPDATE `rating` = VALUES(`rating`)',
                   rating_values)
    c.close()
    db.commit()


def update():
    """
    Update multiple rows in transaction
    """
    ids = random.sample(xrange(1, nrows_total + 1), nrows)
    c = db.cursor()
    for id in ids:
        c.execute('UPDATE `foo` SET `rating` = %s WHERE `id` = %s', [2, id])
    c.close()
    db.commit()


def update_case():
    """
    Update multiple rows with case / when / then
    """
    ids = random.sample(xrange(1, nrows_total + 1), nrows)
    values = [2 for _ in xrange(nrows)]
    c = db.cursor()
    when_statement = ' '.join('WHEN %s THEN %s' % args for args in zip(ids, values))
    in_statement = ','.join(str(i) for i in ids)

    c.execute('''UPDATE `foo` SET `rating` = CASE `id`
                    %s ELSE `rating` END
                 WHERE `id` IN (%s)''' % (when_statement, in_statement))
    c.close()
    db.commit()
