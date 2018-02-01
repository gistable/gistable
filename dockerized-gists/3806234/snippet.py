from threading import Thread
from Queue import Queue
import sqlite3

class MultiThreadOK(Thread):
    def __init__(self, db):
        super(MultiThreadOK, self).__init__()
        self.db=db
        self.reqs=Queue()
        self.start()
    def run(self):
        cnx = sqlite3.Connection(self.db) 
        cursor = cnx.cursor()
        while True:
            req, arg, res = self.reqs.get()
            if req=='--close--': break
            elif req=='--commit--': 
            	cnx.commit()
            	break
            cursor.execute(req, arg)
            if res:
            	
                for rec in cursor:
                    res.put(rec)
                res.put('--no more--')
        cnx.close()
    def execute(self, req, arg=None, res=None):
    	self.reqs.put((req, arg or tuple(), res))
    def select(self, req, arg=None):
        res=Queue()
        self.execute(req, arg, res)
        while True:
            rec=res.get()
            if rec=='--no more--': break
            yield rec
    def commit(self):
    	sql.execute("--commit--")

    def close(self):
        self.execute('--close--')

def sql_exec(command):
    if command.startswith("SELECT"):
        output = []
        for key, value in sql.select(command):
            output.append([key, value])
        return output
    else:
        sql.execute(command)
        return []

if __name__=='__main__':

    db='people.db'

    sql=MultiThreadOK(db)


    sql_exec("create table people(name,first)")
    sql_exec("insert into people values('Czabania','George')")
    
    #The first commit works
    sql.commit()

    sql_exec("insert into people values('Cooper','Jono')")

    #The second commit doesn't =(
    sql.commit()