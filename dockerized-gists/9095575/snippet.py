import random
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    r = requests.get("http://en.wikipedia.org/wiki/List_of_The_Price_Is_Right_pricing_games")
    soup = BeautifulSoup(r.content)
    games = soup.find_all("span", {"class":"mw-headline"})
    while True:
        choice = random.choice(games).text
        if len(choice) <= 1:
            continue
        print choice
        break