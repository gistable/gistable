#! /usr/bin/env python
import os
import psycopg2
import MySQLdb

PG = {
    'name' : 'moodle_rvt_sociales',
    'user' : 'diegueus9',
    'pass' : 'fuseki',
    'host' : 'localhost',
}

MYSQL = {
    'db': 'moodle_rvt_sociales',
    'user': 'root',
    'passwd': 'fuseki',
    'host': 'localhost',
}

TABLES_LIST = [
    'pais',
    'tutor_rvt',
    'tipo_area',
    'administradores',
    'ahijado',
    'contactos',
    'departamento',
    'desempena',
    'ejerce_dp',
    'ejerce_en',
    'ejerce_tv',
    'grupo_interes',
    'institucion',
    'lista_contactos_grupo',
    'municipio',
    'promedio',
    'promedio_categoria',
    'rol_es_mti',
    'tabla_auxiliar_para_borrar_los_que_nunca',
    'tipo_area',
]

def create_pg_connection():
    string = "dbname={name} user={user} password={pass}".format(**PG)
    conn = psycopg2.connect(string)
    cur = conn.cursor()
    return cur

def generate_tsv(table):
    file_ = open('/tmp/{0}.tsv'.format(table), 'w')
    kwargs = {
        'file': file_,
        'table': table,
    }
    cursor = create_pg_connection()
    cursor.copy_to(**kwargs)
    cursor.close()

def import_tsv(table):
    MYSQL.update({'table': table})
    mysql_command = 'mysqlimport --local --compress --user={user} --password={passwd} --verbose --host={host} {db} /tmp/{table}.tsv'.format(**MYSQL)
    os.system(mysql_command)

def create_mysql_connection():
    conn = MySQLdb.connect(**MYSQL)
    cursor = conn.cursor()
    return cursor

def get_mysql_tables():
    cursor = create_mysql_connection()
    cursor.execute(""" SHOW TABLES """)
    result = cursor.fetchall()
    for table in result:
        yield table[0]


if __name__=="__main__":
    TABLES_LIST = []
    for table in get_mysql_tables():
        TABLES_LIST.append(table)
    for table in TABLES_LIST:
        generate_tsv(table)
        import_tsv(table)