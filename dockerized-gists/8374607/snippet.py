from datetime import date
from sqlalchemy import cast, DATE
Match.query.filter(cast(Match.date_time_field, DATE)==date.today()).all()