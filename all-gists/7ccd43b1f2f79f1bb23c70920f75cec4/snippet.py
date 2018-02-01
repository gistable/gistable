import uuid
import random

from afase.models.meta import Base

from sqlalchemy import (
    Column,
    Text,
    Date,
    ForeignKey,
    String,
)
from sqlalchemy.types import (
    TypeDecorator,
    CHAR,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
        relationship,
        validates,
)
# Trap, not really part of the code. Make them explain what it does anyhow.
class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR
    
    # Based on how this class is used below, have them explain why the functions are named as they are.
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)
          
# Trap, they'll skip this, point out that they missed something when they get to "create" function
ALPHABET = '0123456789abcdefghjkmnpqrtvwxyz'
ALPHA_SET = set(ALPHABET)
HEXIES = set('abcdef0123456789')

# Trap, this function should not be part of the data model, it should be internal. See if they catch on it.
def gen_word(count):
    # Bug, shouldn't re-initialize RNG everytime we need it
    r = random.SystemRandom()
    word = ''.join(r.choice(ALPHABET) for x in range(count))
    return word.capitalize()


class Token(Base):
    __tablename__ = 'token'
    id = Column(GUID, primary_key=True)
    link = Column(Text, nullable=False)
    token = Column(String(length=16), nullable=False, unique=True)
    device = relationship('Device')
    cabinet = relationship('Cabinet')

    # Unnecessary, see if they catch why this have an init when the other classes don't. 
    def __init__(self, id, token, link):
        self.id = id
        self.token = token
        self.link = link

    # Simple, let them explain this
    @validates('token')
    def validate_token(self, key, token):
        letters = set(token)
        if not ALPHA_SET.issuperset(letters):
            raise ValueError("Non permitted letter in token")
        return token

    # Incomplete, ask them to add more validations
    @validates('link')
    def validate_link(self, key, link):
        if not link.startswith('https://'):
            raise ValueError("Non https link")

        if link[-1] in ('/', '?'):
            raise ValueError("Link ends in invalid char")

        if link.count("/") != 3:
            raise ValueError("Should have 3 and only 3 slashes in link")

        return link

    def __repr__(self):
        return "<Token(id='{}, token='{}', link='{}')>".format(self.id, self.token, self.link)

    # Make them explain why this code exists. Describe how it will be used.
    # All code exists for a reason, sometimes that reason is that a programmer was drunk.
    @classmethod
    def normalize(cls, token):
        replacements = [('o', '0'),
                        ('l', '1'),('i','1'),
                        ('s', '5'), 
                        ('u', 'v'),
                        ('-',''),('_',''), (' ', '')]
        word  = token.lower()
        for old, new in replacements:
            word = word.replace(old, new)
        return word

    @classmethod
    def create(cls):
        id = uuid.uuid4()
        # Below line is tricky, make them explain what it does.
        base = '-'.join(map(gen_word, [4] * 4))
        link = "https://example.com/{}".format(base)
        token = cls.normalize(base)
        # Note the bug below, ask about subclass of this model.
        return Token(id=id, link=link, token=token)

      
class Site(Base):
    __tablename__ = 'site'
    id = Column(GUID, primary_key=True)
    name = Column(Text, nullable=False)
    customer = Column(Text, nullable=False)
    contact = Column(Text, nullable=True)
    devices = relationship("Device")
    cabinets = relationship("Cabinet")
    # Leave TODO comments in, ask them to improve.
    
    # TODO: Location(GPS)
    # TODO: More contact fields?


class Cabinet(Base):
    __tablename__ = 'cabinet'
    id = Column(GUID, primary_key=True)
    serial = Column(Text, nullable=False)
    revision = Column(Text, nullable=False)

    token = Column(GUID, ForeignKey('token.id'))
    site  = Column(GUID, ForeignKey('site.id'))


class Device(Base):
    __tablename__ = 'device'
    id = Column(GUID, primary_key=True)

    boxid = Column(String(length=12), nullable=False)
    kind = Column(Text, nullable=False)

    token = Column(GUID, ForeignKey('token.id'))

    site = Column(GUID, ForeignKey('site.id'), nullable=True)
    deploy_date = Column(Date, nullable=True)
    retire_date = Column(Date, nullable=True)

    @validates('boxid')
    def validate_token(self, key, boxid):
        if not HEXIES.issuperset(set(boxid)):
            raise ValueError("Non hex letter in boxid")
        if not len(boxid) == 12:
            raise ValueError("Box ID should be 12 long, no more, no less")
        return boxid

