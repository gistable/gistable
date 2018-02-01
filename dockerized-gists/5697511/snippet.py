import logging
import cStringIO
import csv

DEBUG = False

def data2csv(data):
    si = cStringIO.StringIO()
    cw = csv.writer(si, delimiter='\t',lineterminator="\n")
    for row in data:
        r = [ (x is None and '\N' or x) for x in row]
        cw.writerow(r)
    si.seek(0)
    return si # .getvalue()

def upsert(cursor, table_name, selector_fields, setter_fields, data):

    csv_data = data2csv(data)

    sql_template = """
        WITH updates AS (
            UPDATE %(target)s t
                SET %(set)s        
            FROM source s
            WHERE %(where_t_pk_eq_s_pk)s 
            RETURNING %(s_pk)s
        )
        INSERT INTO %(target)s (%(columns)s)
            SELECT %(source_columns)s 
            FROM source s LEFT JOIN updates t USING(%(pk)s)
            WHERE %(where_t_pk_is_null)s
            GROUP BY %(s_pk)s
    """
    statement = sql_template % dict(
        target = table_name,
        set = ',\n'.join(["%s = s.%s" % (x,x) for x in setter_fields]),
        where_t_pk_eq_s_pk = ' AND '.join(["t.%s = s.%s" % (x,x) for x in selector_fields]),
        s_pk = ','.join(["s.%s" % x for x in selector_fields]),
        columns = ','.join([x for x in selector_fields+setter_fields]),
        source_columns = ','.join(['s.%s' % x for x in selector_fields+setter_fields]), 
        pk = ','.join(selector_fields),
        where_t_pk_is_null = ' AND '.join(["t.%s IS NULL" % x for x in selector_fields]),
        t_pk = ','.join(["t.%s" % x for x in selector_fields]))

    if DEBUG: 
        logging.debug(statement) 

    # with cursor as cur:
    cur = cursor
    cur.execute('CREATE TEMP TABLE source(LIKE %s INCLUDING ALL) ON COMMIT DROP;' % table_name);  
    cur.copy_from(csv_data, 'source', columns=selector_fields+setter_fields)
    cur.execute(statement)
    cur.execute('DROP TABLE source')
    csv_data.close()