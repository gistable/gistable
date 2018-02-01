from cqlengine import columns
from cqlengine.models import Model

class Users(Model):
  firstname = columns.Text()
  age = columns.Integer()
  city = columns.Text()
  email = columns.Text()
  lastname = columns.Text(primary_key=True)
  def __repr__(self):
    return 'user(firstname=%s, age=%d)' % (self.firstname, self.age)


from cqlengine import connection

connection.setup(['127.0.0.1'], "demo")

from cqlengine.management import sync_table

sync_table(Users)

Users.create(firstname='Bob', age=35, city='Austin', email='bob@example.com', lastname='Jones')

q=Users.get(lastname='Jones')

print q

q.update(age=36)

print q

q.delete()

q=Users.objects()

for i in q: print i
