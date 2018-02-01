#!/usr/bin/env python3
#
# Usage: python3 uber.py ~/Downloads/Takeout/Mail/Uber.mbox
#
# Dependencies: Python 3.4+
#
# How to get the .mbox export:
#
# In Gmail, create a filter that applies the label "Uber" to emails matching:
#
#   from:(uber.com) subject:("uber ride receipt" OR "trip with uber" OR "ride with uber")
#
# Apply the filter to your past emails. Then, go to:
#
#   https://takeout.google.com/settings/takeout
#
# Export your Mail data, selecting just the label "Uber".
# Google will send you an email containing an archive.
# Point this script at its contents.
#
import sys
import re
import mailbox
import email.utils
from datetime import datetime
from collections import defaultdict

def parse_amount(body):
    # Uber has changed their email format over the years.
    # This should find the amount charged for emails from 2011-2016 at least.
    for amount in re.findall(r'([$]\d+(?:[.]\d+)?) has been charged', body):
        return amount
    for amount in re.findall(r'(?:Billed to Card:?|Amount Charged:) +\(([^)]+)\)', body):
        return amount
    for amount in re.findall(r'Billed [Tt]o Card: ([$]\d+(?:[.]\d+)?)', body):
        return amount
    for amount in re.findall(r'Total Fare: +([$]\d+(?:[.]\d+)?)', body):
        return amount
    for amount in re.findall(r'^\s*Total: +([$]\d+(?:[.]\d+)?)', body):
        return amount
    for attrs, amount in re.findall(r'<td\s([^>]+)>\s*([$]\d+(?:[.]\d+)?)\s*<', body):
        # If you're debugging a newer table-based email format, it may help to uncomment:
        # print(attrs, amount)
        if 'final-charge' in attrs or 'totalPrice' in attrs:
            return amount

def extract_trips(messages):
    skipped = 0
    for msg in messages:
        if 'uber' not in msg['From'] or ':' in msg['Subject']:
            continue

        body = msg.get_payload()[0].get_payload(decode=True).decode()
        if 'you have earned $10 in Uber credit' in body:
            continue

        date = email.utils.parsedate_to_datetime(msg['Date'])
        amount = parse_amount(body)

        if amount is None:
            skipped += 1
        else:
            amount = float(amount[1:])
            yield (date, amount)

    if skipped:
        print("Skipped {} message(s) where I couldn't parse a trip amount.".format(skipped))
        # If you want to debug this:
        # print(body)
        # ...and add a new regex to `parse_amount` above.

def summarize_trips(trips):
    trips_by_year = defaultdict(int)
    amount_by_year = defaultdict(float)
    total_trips = 0
    total_amount = 0
    for date, amount in trips:
        total_trips += 1
        total_amount += amount
        year = date.astimezone().year
        trips_by_year[year] += 1
        amount_by_year[year] += amount

    print("You've spent a total of ${:.2f} on {} trip(s) with Uber.\n"
        .format(total_amount, total_trips))

    start_year = min(trips_by_year)
    end_year = max(max(trips_by_year), email.utils.localtime().year)
    for year in range(start_year, end_year + 1):
        count = trips_by_year[year]
        amount = amount_by_year[year]
        print("{:7}   ${:8.2f}   {:3} trip(s)".format(year, amount, count))

if __name__ == '__main__':
    mbox = mailbox.mbox(sys.argv[1], create=False)
    trips = list(extract_trips(mbox))
    summarize_trips(trips)
