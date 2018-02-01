DELETE = "delete"
UPDATE = "update"
SELECT = "select"
INSERT = "insert"

QUOTE = "'"


def format_parameter(parameter, value):
    return "%s = %s" % (parameter, determine_quote(value))

def determine_quote(value):
    if isinstance(value, basestring):
        return QUOTE + value + QUOTE
    return value

def generate_parameters(conditions, delimiter=","):
    return delimiter.join([format_parameter(parameter, value)
                      for parameter, value in conditions.items()])


def select(table_name, fields="*", where=None):
    yield "SELECT"
    yield ",".join(fields) or "*"
    yield "FROM"
    yield table_name
    if where:
        yield "WHERE"
        yield generate_parameters(where, delimiter="AND")


def delete(table_name, where=None):
    yield "DELETE"
    yield "FROM"
    yield table_name
    if where:
        yield "WHERE"
        yield generate_parameters(where, delimiter="AND")

def update(table_name, updates, where=None):
    yield "UPDATE"
    yield table_name
    yield "SET"
    yield generate_parameters(updates)
    if where:
        yield "WHERE"
        yield generate_parameters(where, delimiter="AND")

def insert(table_name, updates):
    yield "INSERT"
    yield table_name
    yield "(%s)" % ", ".join(updates.keys())
    yield "VALUES"
    yield "(%s)" % ", ".join(map(determine_quote, updates.values()))


class SqlBuilder(object):

    def __init__(self):
        self.table_name = None
        self.fields = []
        self.conditions = {}
        self.updates = {}
        self.clause = None

    def __getattr__(self, attr):
        self.table_name = attr
        return self

    def select(self, *fields):
        self.fields = fields
        self.clause = SELECT
        return self

    def where(self, **conditions):
        self.conditions = conditions
        self.clause = SELECT
        return self

    def delete(self, **conditions):
        self.conditions = conditions
        self.clause = DELETE
        return self

    def update(self, **updates):
        self.updates = updates
        self.clause = UPDATE
        return self

    def insert(self, **updates):
        self.updates = updates
        self.clause = INSERT
        return self

    def as_sql(self):
        builders = {
            SELECT: lambda: select(self.table_name, self.fields, self.conditions),
            DELETE: lambda: delete(self.table_name, self.conditions),
            UPDATE: lambda: update(self.table_name, self.updates, self.conditions),
            INSERT: lambda: insert(self.table_name, self.updates),
        }

        return " ".join(builders[self.clause]())

    __repr__ = as_sql


db = SqlBuilder()

print db.users.delete(id=33)
print db.users.select("username").where(username="fatih")
print db.users.where(username="fatih").update(is_active=1)
print db.users.insert(username="foo", password="test")

"""
Output:

    DELETE FROM users WHERE id = 33
    SELECT username FROM users WHERE username = 'fatih'
    UPDATE users SET is_active = 1 WHERE username = 'fatih'
    INSERT users (username, password) VALUES ('foo', 'test')

"""