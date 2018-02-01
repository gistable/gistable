import psycopg2
import psycopg2.extensions
from select import select
from twisted.internet import threads

class AsyncNotify():
    """
    based on http://divillo.com/, adapted to newer psycopg version
    
    Class to trigger a function via PostgreSQL NOTIFY messages. 
    Refer to the documentation for more information on LISTEN, NOTIFY and UNLISTEN. 
    http://www.postgresql.org/docs/8.3/static/sql-notify.html
    """

    timeout = 3
    
    def __init__(self, dsn):
        """The dsn is passed here. This class requires the psycopg2 driver."""
        self.conn = psycopg2.connect(dsn)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.curs = self.conn.cursor()
        self.__listening = False

    def __listen(self):
        if self.__listening:
            return 'already listening!'
        else:
            self.__listening= True
            while self.__listening:
                if select([self.conn],[],[],self.timeout) != ([],[],[]):
                    self.conn.poll()
                    while self.conn.notifies:
                        pid, notify = self.conn.notifies.pop()
                        self.gotNotify(pid, notify)

    def addNotify(self, notify):
        """Subscribe to a PostgreSQL NOTIFY"""
        sql = "LISTEN %s" % notify
        self.curs.execute(sql)

    def removeNotify(self, notify):
        """Unsubscribe a PostgreSQL LISTEN"""
        sql = "UNLISTEN %s" % notify
        self.curs.execute(sql)

    def stop(self):
        """Call to stop the listen thread"""
        self.__listening = False

    def run(self):
        """Start listening in a thread and return that as a deferred"""
        return threads.deferToThread(self.__listen)

    def gotNotify(self, pid, notify):
        """Called whenever a notification subscribed to by addNotify() is detected.
        Unless you override this method and do someting this whole thing is rather pointless."""
        pass
