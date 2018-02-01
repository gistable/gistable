#!/usr/bin/env python
import os
os.environ.setdefault('SETTINGS_MODULE', 'data.settings_modules.vagrant')

from flask_script import Manager
from data.settings import DATABASES
from web import app

manager = Manager(app)

@manager.command
def dbshell():
    db = DATABASES['mydb']
    args = ["psql", "--host=%s" % db['HOST'], "--user=%s" % db['USER'],
            "--dbname=%s" % db['NAME']]
    os.execvp("psql", args)

if __name__ == "__main__":
    manager.run()