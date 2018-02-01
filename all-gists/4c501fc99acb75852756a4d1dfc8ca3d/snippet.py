#!/usr/bin/env python
from bs4 import BeautifulSoup
from twilio.rest import TwilioRestClient
import json
import os
import re
import requests


url = 'https://postmates.com/los-angeles'


def sendText(body):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_number = os.environ['TWILIO_PHONE_NUMBER']
    number_file = os.environ['POSTMATES_NUMBERS']

    client = TwilioRestClient(account_sid, auth_token)

    with open(number_file, 'r') as numbers:
        for number in numbers:
            client.messages.create(body=body, to=number, from_=twilio_number)


def extractFreeFoodFromSoup(soup):
    regex = re.compile('free')
    strings = list(soup.stripped_strings)
    freeFood = [s for s in strings if regex.match(s.lower())]
    return freeFood


def hasNewFreeFood(freeFood):
    try:
        foodFile = open('/tmp/freefood', 'r+')
        previousFreeFood = json.load(foodFile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        foodFile = open('/tmp/freefood', 'w+')
        previousFreeFood = []

    foodFile.seek(0)
    foodFile.truncate()
    json.dump(freeFood, foodFile)
    foodFile.close()

    return freeFood != previousFreeFood


def main():
    postmatesPage = requests.get(url)
    soup = BeautifulSoup(postmatesPage.text, 'html.parser')

    freeFood = extractFreeFoodFromSoup(soup)

    if hasNewFreeFood(freeFood):
        sendText('Free Postmates!\n\n' + '\n'.join(freeFood))


if __name__ == '__main__':
    main()