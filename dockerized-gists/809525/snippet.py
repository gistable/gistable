# -*- coding: utf8 -*-

import datetime, os

class MongoDbExporter(object):

    """
    a tiny wrapper for the bash utility named mongoexporter.
    """

    LOCK_FILE = 'log.txt'
    
    def __init__(self, config):
        self.host       = config.get("host"),
        self.database   = config.get("database")
        self.collection = config.get("collection")
        self.backup_dir = config.get("backup_dir")
        
        if self.backup_dir:
            if not self.backup_dir.endswith('/'):
                self.backup_dir += "/"
            self.backup_file = self.backup_dir + self.__generateBackupDate() + ".json"
            if not os.access(os.getcwd(), os.W_OK):
                raise Exception("i cannot create lock file. make this directory writable.")
        
        self.__controlConfig(config)
    
    def backUp(self):   
        print "started"
        
        self.__createLock()
        command = "mongoexport -c %s -d %s >> %s" % (self.collection,
                                                     self.database,
                                                     self.backup_file)
        os.system(command)
        self.__acquireLock()
        
    def __controlConfig(self, config):
        for config_variable in config.iterkeys():
            if config.get(config_variable) == None:
                raise Exception("%s cannot be empty" % config_variable)
        
        if not config.get("backup_dir").startswith("/"):
            raise Exception("backup_dir variable must be absolute.")
        
        if not os.path.exists(config.get("backup_dir")):
            print "backup directory doesnt exist, trying to create."
            os.makedirs(config.get("backup_dir"))

    def __generateBackupDate(self):
        dt = datetime.datetime.now()
        return datetime.datetime.strftime(dt, "%Y-%m-%d-%H-%M")
        
    def __createLock(self):
        self.__controlLock()
        print "creating lock file"
        fp = open(MongoDbExporter.LOCK_FILE, 'w')
        fp.close()
        
    def __acquireLock(self):
        print "lock acquired"
        os.remove(MongoDbExporter.LOCK_FILE)
    
    def __controlLock(self):
        if os.path.exists(MongoDbExporter.LOCK_FILE):
            raise Exception("an alive dumper instance exists. try later.")

if __name__ == '__main__':
    backup = MongoDbExporter({
        "host"       : "localhost",
        "database"   : "test",
        "collection" : "logs",
        "backup_dir" : "/home/emre/tmp/"
    })
    
    backup.backUp()