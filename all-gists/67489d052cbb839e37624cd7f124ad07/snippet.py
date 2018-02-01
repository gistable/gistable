#!/usr/bin/python
import requests
from datetime import datetime

# Config:
source = "THR,IKA"
destination = "BND"
start_str = "2018/01/17"
end_str = "2018/01/23"
sthreshold = 130  # hezar toman, color (soft) threshold
hthreshold = 170  # toggle (hard) threshold

# Request:
r = requests.post(
    url='https://sepehr360.com/fa/Api/CalendarApi/SetFlightMonthHistory',
    data={
        "source": source,
        "destination": destination,
        "currencyType": "IRR"
    })

result = r.json()
start = datetime.strptime(start_str, "%Y/%m/%d")
end = datetime.strptime(end_str, "%Y/%m/%d")
filtered_result = [
    i for i in result['Arrival']
    if (datetime.strptime(i['FlightDate'][:10], "%Y-%m-%d") >= start
        and datetime.strptime(i['FlightDate'][:10], "%Y-%m-%d") <= end)
]

event = min(filtered_result, key=lambda ev: int(ev['Price']))

if float(event['Price']) <= hthreshold:
    print(
        "✈ <font color='{color}'>{source}->{dest}: {date}, {currency}{price:,.0f}</font>".
        format(
            source=source[:3],
            dest=destination[:3],
            date=event["Date"],
            price=float(event["Price"]) * 10 * 1000,
            currency="﷼",
            color='green'
            if float(event["Price"]) <= sthreshold else 'darkgrey'))
else:
    print("<font color='black'> <font>")