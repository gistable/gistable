from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:', echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Float

class User(Base): 
	__tablename__ = 'users'   
	id = Column(Integer, primary_key=True)
 	name = Column(String)
 	fullname = Column(String)
 	balance = Column(Float)
 	group = Column(String)
	def __init__(self, name, fullname, balance, group):
		self.name = name
		self.fullname = fullname
		self.balance = balance
		self.group = group

user1 = User('Bob', 'Big Bob', 1000000.00, 'Mob')
user2 = User('Linda', 'Linda Lu', 100.50, 'Diner')
user3 = User('Lil Bob', 'Bobby Jr', 100500.00, 'Mob')
user4 = User('Rachael', 'Rachael Rach', 125.50, 'Personal')

from sqlalchemy.orm import session maker
Session = sessionmaker(bind=engine)
db = Session()

db.add(user1)
db.add(user2)
db.add(user3)
db.add(user4)
db.commit()

db.query(User).all()

for user in db.query(User).all():
	print user.name, user.balance

from sqlalchemy import func
from sqlalchemy.sql import label

db.query(User.group,
	label('members', func.count(User.id)),
	label('total_balance', func.sum(User.balance))).group_by(User.group).all()

results = db.query(User.group,
	label('members', func.count(User.id)),
	label('total_balance', func.sum(User.balance))).group_by(User.group).all()

for result in results:
	print "%s has %i members with a balance of %d" % (result.group, result.members, result.total_balance)