""" 
Nice fake South database driver in case you are mixing supported/unsupported databases.

Usage: Update your settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'mydb',
        'USER': 'mydb',
        'PASSWORD': '',
    },
    'mongodb': {
        'ENGINE': 'django_mongokit.mongodb',
        'NAME': 'mymongodb',
    },
}

SOUTH_DATABASE_ADAPTERS = {
    'mongodb': 'fakesouth',
}
"""

class DatabaseOperations(object):
    def __init__(self, *args):
        pass
        
    def connection_init(*args):
        pass
        
    def add_column(self):
        pass

    def alter_column(self):
        pass
    
    def clear_table(self):
        pass
    
    def commit_transaction(self):
        pass
    
    def create_index(self):
        pass
    
    def create_primary_key(self):
        pass
    
    def create_table(self):
        pass
    
    def create_unique(self):
        pass
    
    def delete_column(self):
        pass
    
    def delete_foreign_key(self):
        pass
    
    def delete_primary_key(self):
        pass
    
    def delete_table(self):
        pass
    
    def delete_unique(self):
        pass
    
    def execute(self):
        pass
    
    def execute_many(self):
        pass
    
    def rename_column(self):
        pass
    
    def rename_table(self):
        pass
    
    def rollback_transaction(self):
        pass
    
    def send_create_signal(self):
        pass
    
    def start_transaction(self):
        pass