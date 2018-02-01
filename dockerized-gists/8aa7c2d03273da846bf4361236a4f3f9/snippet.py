"""A tool for saving files to and from a postgresql db.
"""
import os
import sys
import argparse
import psycopg2

db_conn_str = "postgresql://username:password@localhost:5432/dbname"
create_table_stm = """
CREATE TABLE files (
    id serial primary key,
    orig_filename text not null,
    file_data bytea not null
)
"""

def main(argv):
    parser = argparse.ArgumentParser()
    parser_action = parser.add_mutually_exclusive_group(required=True)
    parser_action.add_argument("--store", action='store_const', const=True, help="Load an image from the named file and save it in the DB")
    parser_action.add_argument("--fetch", type=int, help="Fetch an image from the DB and store it in the named file, overwriting it if it exists. Takes the database file identifier as an argument.", metavar='42')
    parser.add_argument("filename", help="Name of file to write to / fetch from")
    args = parser.parse_args(argv[1:])

    conn = psycopg2.connect(db_conn_str)
    curs = conn.cursor()
    if args.store:
        with open(args.filename,'rb') as f:
            filedata = f.read()
            curs.execute("INSERT INTO files(id, orig_filename, file_data) VALUES (DEFAULT,%s,%s) RETURNING id", (args.filename, filedata))
            returned_id = curs.fetchone()[0]
        print("Stored {0} into DB record {1}".format(args.filename, returned_id))
        conn.commit()

    elif args.fetch is not None:
        with open(args.filename,'wb') as f:
            curs.execute("SELECT file_data, orig_filename FROM files WHERE id = %s", (int(args.fetch),))
            (file_data, orig_filename) = curs.fetchone()
            f.write(file_data)
        print("Fetched {0} into file {1}; original filename was {2}".format(args.fetch, args.filename, orig_filename))

    conn.close()

if __name__ == '__main__':
    main(sys.argv)
