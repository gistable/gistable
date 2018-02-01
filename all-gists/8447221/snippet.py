#!/usr/bin/env python

import os
import sqlite3

from csvkit import table, CSVKitWriter
from csvkit.cli import CSVKitUtility
from csvkit.sql import make_create_table_statement, make_table


class CSVQuery(CSVKitUtility):
    description = "Issue SQL queries against CSV data"

    def add_arguments(self):
        self.argparser.add_argument('query', type=unicode)

    def main(self):
        tabname = os.path.splitext(os.path.basename(self.args.file._lazy_args[0]))[0]
        tab = table.Table.from_csv(self.args.file, name=tabname, **self.reader_kwargs)
        stmt = make_create_table_statement(make_table(tab), dialect='sqlite')
        conn = sqlite3.connect(':memory:')
        c = conn.cursor()
        c.execute(stmt)
        for row in tab.to_rows():
            vals = ','.join(['?'] * len(row))
            prepared = "INSERT INTO %s VALUES(%s)" % (tab.name, vals)
            c.execute(prepared, row)
        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        for row in c.execute(self.args.query):
            output.writerow(row)


def launch_new_instance():
    utility = CSVQuery()
    utility.main()


if __name__ == '__main__':
    launch_new_instance()
