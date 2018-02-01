from multiprocessing import Process
from django.core import serializers
from django.core.management import call_command
from StringIO import StringIO

def dump_database():
    sio = StringIO()
    call_command('dumpdata', stdout=sio, natural=True)
    return sio.getvalue()

def call_command_with_db(dbdump, *args, **kwargs):
    objects = serializers.deserialize('json', dbdump)
    for obj in objects:
        obj.save()
    return call_command(*args, **kwargs)

def do_something():
    dbdump = dump_database()
    process = Process(target=call_command_with_db, args=(dbdump, 'runserver',))
    process.start()
