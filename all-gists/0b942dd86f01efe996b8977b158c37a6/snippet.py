""" script to gather the average crrency exchange rate from fixer.io """

from urllib.parse import urlencode
from datetime import date, timedelta
import requests

def currency_conversion_rate(base, target, that_date='latest'):
    """
    get the currency conversion rate for the specific date
    """

    main_api = 'http://api.fixer.io/{}?'.format(that_date)
    url = main_api + urlencode({'base':base})
    json_data = requests.get(url).json()

    try:
        result = json_data['rates'][target]
    # except requests.exceptions.ConnectionError:
        # result = "Connection Error"
    except KeyError:
        result = 0.00

    return result

def main(base, target, start_date, end_date):

    step = timedelta(days=1)

    total_days = 0
    total_amount_sum = 0

    while start_date < end_date:
        that_date = start_date.strftime("%Y-%m-%d")
        amount = currency_conversion_rate(base, target, that_date)
        if amount != 0:
            # because on fixer.io gives exchange rates for working days
            # so we're only considering the days when we do have a rate available
            # for more on this: https://github.com/hakanensari/fixer-io/issues/47
            total_amount_sum += amount
            total_days += 1

        print(that_date, amount)


        start_date += step

    print(total_amount_sum/total_days)

if __name__ == '__main__':
    START_DATE = date(2017, 8, 1)
    END_DATE = date(2017, 8, 15)
    main('USD', 'INR', START_DATE, END_DATE)
