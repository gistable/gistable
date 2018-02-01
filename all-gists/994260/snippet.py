"""
remove_foreign_keys.py

Removes all the foreign key constraints in a django project's MySQL database.

NO FOREIGN KEYS = NO FOREIGN KEY HEADACHES 
(of course if you are using anything other than the django ORM its likely to cause other headaches)

Before running this script be sure your django settings module is available
to your environment.

export DJANGO_SETTINGS_MODULE=yoursite.settings
"""

import logging
from django.conf import settings


def get_foreign_key_names(database_name):
    from django.db import connection
    cursor = connection.cursor()

    cursor.execute("SELECT `table_schema`, `table_name`, `constraint_name` FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY' AND table_schema = %s;", [database_name])
    return cursor.fetchall()

def remove_foreign_key(schema_name, table_name, key_name):
    from django.db import connection, transaction
    cursor = connection.cursor()

    logging.info("Removing foreign key %s from %s.%s" % (key_name, schema_name, table_name))
    sql = "ALTER TABLE %s.%s DROP FOREIGN KEY %s;" %  (schema_name, table_name, key_name)
    cursor.execute(sql)
    transaction.commit_unless_managed()

def remove_all_foreign_keys(database_name):
    foreign_keys = get_foreign_key_names(database_name)
    logging.info("Removing all foreign key constraints from database: %s" % database_name)
    for schema_name, table_name, key_name in foreign_keys:
      remove_foreign_key(schema_name, table_name, key_name)

db_name = settings.DATABASES['default']['NAME']
remove_all_foreign_keys(db_name)