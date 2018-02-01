#project/project/__init__.py
import project.settings
import pymongo

THE_MONGO_CLIENT = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)

#project/project/settings.py
INSTALLED_APPS += 'utils'

MONGO_HOST = 'localhost' #default
MONGO_PORT = 27017 #default

#project/utils/mongo_tools.py
from project import THE_MONGO_CLIENT

def get_mongo_db(db_name):
  return THE_MONGO_CLIENT[db_name]

#project/app/views.py
# (example)
from utils.mongo_tools import get_mongo_db

def example_view(request):
  db = get_mongo_db('a_database')
  # do request stuff