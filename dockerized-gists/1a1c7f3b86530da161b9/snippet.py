class ConnectionPool():
    """
    Usage:
        conn_pool = nmi_mysql.ConnectionPool(config)

        db = conn_pool.get_connection()
        db.query('SELECT 1', [])
        conn_pool.return_connection(db)

        conn_pool.close()
    """
    def __init__(self, conf, max_pool_size=20):
        self.conf = conf
        self.max_pool_size = max_pool_size
        self.initialize_pool()

    def initialize_pool(self):
        self.pool = Queue(maxsize=self.max_pool_size)
        for _ in range(0, self.max_pool_size):
            self.pool.put_nowait(DB(self.conf, True))

    def get_connection(self):
        # returns a db instance when one is available else waits until one is
        db = self.pool.get(True)

        # checks if db is still connected because db instance automatically closes when not in used
        if not self.ping(db):
            db.connect()

        return db

    def return_connection(self, db):
        return self.pool.put_nowait(db)

    def close(self):
        while not self.is_empty():
            self.pool.get().close()

    def ping(self, db):
        data = db.query('SELECT 1', [])
        return data

    def get_initialized_connection_pool(self):
        return self.pool

    def is_empty(self):
        return self.pool.empty()