from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker, joinedload

# For this example we will use an in-memory sqlite DB.
# Let's also configure it to echo everything it does to the screen.
engine = create_engine('sqlite:///:memory:', echo=True)

# The base class which our objects will be defined on.
Base = declarative_base()

# Our User object, mapped to the 'users' table
class User(Base):
    __tablename__ = 'users'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(Integer, primary_key=True)

    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    # Lets us print out a user object conveniently.
    def __repr__(self):
       return "<User(name='%s', fullname='%s', password'%s')>" % (
                               self.name, self.fullname, self.password)

# The Address object stores the addresses 
# of a user in the 'adressess' table.
class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)

    # Since we have a 1:n relationship, we need to store a foreign key 
    # to the users table.
    user_id = Column(Integer, ForeignKey('users.id'))

    # Defines the 1:n relationship between users and addresses.
    # Also creates a backreference which is accessible from a User object.
    user = relationship("User", backref=backref('addresses'))

    # Lets us print out an address object conveniently.
    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address


# Create all tables by issuing CREATE TABLE commands to the DB.
Base.metadata.create_all(engine) 

# Creates a new session to the database by using the engine we described.
Session = sessionmaker(bind=engine)
session = Session()

# Let's create a user and add two e-mail addresses to that user.
ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
ed_user.addresses = [Address(email_address='ed@google.com'), Address(email_address='e25@yahoo.com')]

# Let's add the user and its addresses we've created to the DB and commit.
session.add(ed_user)
session.commit()

# Now let's query the user that has the e-mail address ed@google.com
# SQLAlchemy will construct a JOIN query automatically.
user_by_email = session.query(User)\
    .filter(Address.email_address=='ed@google.com')\
    .first()

print user_by_email

# This will cause an additional query by lazy loading from the DB.
print user_by_email.addresses


# To avoid querying again when getting all addresses of a user,
# we use the joinedload option. SQLAlchemy will load all results and hide
# the duplicate entries from us, so we can then get for
# the user's addressess without an additional query to the DB.
user_by_email = session.query(User)\
    .filter(Address.email_address=='ed@google.com')\
    .options(joinedload(User.addresses))\
    .first()

print user_by_email
print user_by_email.addresses

