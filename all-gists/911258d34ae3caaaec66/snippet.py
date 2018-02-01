import requests
import json
import os

FILENAME = 'goodquotes.json'

def fetchQuotes():
    for page in range(1, 101):
        quotes_on_page = []
        url = "https://api.import.io/store/data/cd22ca4b-5d29-4ff3-9c69-cd372563c051/_query?input/webpage/url=https%3A%2F%2Fwww.goodreads.com%2Fquotes%3Fpage%3D" + str(page) + "&_user=2f7d8fb2-391c-4ddf-823c-633134603fc0&_apikey=T67gIWtTHeLU73sx95D8jtFpWs33Qhe7Ym1xn95IxYTvWjyhD5vM9lK0clQVSvaZ%2BRvZilxmHoD0llECgxGE9Q%3D%3D"
        r = requests.get(url)
        if r.status_code == 200:
            try:
                for result in json.loads(r.text)['results']:
                    q = {}
                    q['quote'] = result['text_1']
                    q['author'] = result['text_4']

                    quotes_on_page.append(q)
                except KeyError:
                    print 'No results found in the response'
                    print r.text

            updateFile(quotes_on_page)

            print 'Imported ' + str(len(quotes_on_page)) + ' quotes from ' + str(page) + '.'

    print '>>> saved to ' + FILENAME
    print 'Completed.'


def updateFile(new_quotes):
    with open(FILENAME, 'r+') as f:
        try:
            quotes = json.load(f)
            quotes += new_quotes
        except ValueError:
            quotes = new_quotes

        f.seek(0)
        f.write(json.dumps(quotes, indent=2, sort_keys=True))
        f.truncate() 

def main():
    fetchQuotes()

if __name__ == "__main__":
    main()