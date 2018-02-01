# The trick is to pass timedelta object as a sort key and not to use cmp() function

import datetime

        def date_key(a):
            """
            a: date as string
            """
            a = datetime.datetime.strptime(a, '%d.%m.%Y').date()
            return a

        sorted_dates = sorted(sorted_dates, key=date_key)
