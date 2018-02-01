from datetime import datetime, timedelta

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

NOW = datetime.utcnow()
DBSession = scoped_session(sessionmaker())
Base = declarative_base()

class Status(Base):
    __tablename__ = 'status'
    id = sa.Column(sa.Integer, primary_key=True)
    submit_time = sa.Column(sa.DateTime, default=datetime.now())
    
    def __repr__(self):
        return self.__unicode__();
    
    def __unicode__(self):
        return unicode(self.submit_time)
    
engine = sa.create_engine("sqlite://")
engine.echo = False
Base.metadata.bind = engine
Base.metadata.create_all()
DBSession.configure(bind=engine)
session = DBSession()

for h in xrange(1,25):
    for _ in xrange(h % 4):
        session.add(Status(submit_time=NOW - timedelta(hours=h)))
        
session.commit()

last_24h_submits_count = []
for h in xrange(1,25):
    left = NOW - timedelta(seconds=h*3600-1)
    right = NOW - timedelta(hours=h-1)
    count = session.query(Status).filter(Status.submit_time.between(left, right)).count()
    status = session.query(Status).filter(Status.submit_time.between(left, right)).all()
    print "[From %s to %s] count=%d status=%s" % (left, right, count, status)
    last_24h_submits_count.append(count)
    
print last_24h_submits_count