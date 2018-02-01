from datetime import datetime
import redis
import random
import sqlite3

BROKER_HOST = "localhost"  # Maps to redis host.
REDIS_PASSWORD = None
KEY_PREFIX = "speed_"
ALPHABETE = "qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM"
SQLITE_DB = ":memory:"


redis = redis.Redis(
                host=BROKER_HOST,
                password=REDIS_PASSWORD,
            )



start_time = None

def showtime(message):
    global start_time
    if not start_time:
        start_time = datetime.now()
    td = datetime.now() - start_time
    sec = td.seconds
    micsec = td.microseconds / 1000
    print "%s.%s sec: %s" % (sec, micsec, message)
    start_time = datetime.now()
    
def generate_key(key_length=10):
    return "".join([random.choice(ALPHABETE) for x in range(key_length)])

def generate_data():
    return [(generate_key(), generate_key()) for x in range(10**3)]


class SQLiteDB(object):

    def __init__(self):
        self.cn = sqlite3.connect(SQLITE_DB)
        self.cur = self.cn.cursor()
        self.cur.execute("CREATE TABLE T1 (key1 varchar(100), val varchar(100), PRIMARY KEY (key1) )")
        self.cn.commit()

    def __del__(self):
        self.cur.execute("DROP TABLE T1")
        self.cn.commit()

    def clear(self):
        self.cur.execute("DELETE FROM T1")
        self.cn.commit()

    def save(self, data):
        self.cur.executemany("INSERT INTO T1(key1, val) VALUES (?, ?)", data)
        self.cn.commit()

    def get_val(self, key):
        self.cur.execute("SELECT val FROM T1 where key1='%s'" % key)
        row = self.cur.fetchone()
        return row[0]

    def keys(self, pattern):
        self.cur.execute("SELECT key1 FROM T1 where key1 like '%s%%'" % pattern)
        #print "SELECT key1 FROM T1 where key1 like '%s%%'" % pattern
        return [row[0] for row in self.cur]

class RedisDB(object):

    def __init__(self):
        self.clear()

    def __del__(self):
        self.clear()

    def clear(self):
        keys = redis.keys(KEY_PREFIX+"*")
        for key in keys:
            redis.delete(key)

    def save(self, data):
        for key, val in data:
            redis.set(KEY_PREFIX+key, val)

    def get_val(self, key):
        return redis.get(KEY_PREFIX+key)

    def keys(self, pattern):
        return redis.keys(KEY_PREFIX+pattern+"*")


def run_test(db):
    showtime("Start")
    data = generate_data()
    showtime("GENERATE DATA end")
    for x in range(100):
        db.save(data)
        db.clear()
    showtime("INSERT TEST end")
    db.save(data)
    for x in xrange(10**5):
        dt = random.choice(data)
        val = db.get_val(dt[0])
        assert val == dt[1]
    showtime("READ TEST end")

    pattern = data[0][0]
    keys = db.keys(pattern)
    assert len(keys), 1
    
    for x in xrange(10**3):
        pattern = generate_key(2)
        keys = db.keys(pattern)
    showtime("KEYS end")

    db.clear()
    print "END!!!!!!!!!!!!!"

def main():
    print "SQLite TEST---------------------------------"
    run_test(SQLiteDB())
    print "RedisDB TEST---------------------------------"
    run_test(RedisDB())

main()