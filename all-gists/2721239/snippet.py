from fabric.api import local

def get_db_dump():
    local('scp username@host.mozilla.org:/data/www/sumodump.sql.gz .')
    local('gunzip sumodump.sql.gz')

def load_dump():
    local('mysql -e "DROP DATABASE kitsune;"')
    local('mysql -e "CREATE DATABASE kitsune;"')
    local('mysql kitsune < sumodump.sql')

def schematic():
    local('schematic migrations')

def anonymize():
    local('mysql kitsune < scripts/anonymize.sql')

def refresh_db():
    get_db_dump()
    load_dump()
    anonymize()
    schematic()

