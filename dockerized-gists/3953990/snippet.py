#http://stackoverflow.com/questions/7075828/make-sqlalchemy-use-date-in-filter-using-postgresql

from sqlalchemy import Date, cast
from datetime import date

my_date = (session.query(MyObject)
      .filter(cast(MyObject.date_time, Date) == date.today())
      .all())


#or , just like sql

query = session.query(MyObject).filter(MyObject.create_time >= '2012-10-26')

query = (session.query(MyObject)
         .filter(and_(MyObject.create_time >='2012-10-25', MyObject.create_time <= '2012-10-26')))

query = (session.query(MyObject)
        .filter(MyObject.create_time.between('2012-10-25', '2012-10-26')))
