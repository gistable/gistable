from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime, timedelta
from time import sleep
import sys
import csv

# CONSTANTS
ESPN_URL = "http://scores.espn.go.com"

def make_soup(url):
    return BeautifulSoup(urlopen(url), "lxml")


def get_games(date):
    """
    Gets all the play-by-play URLs for a given date (YYYYMMDD).
    Fair warning: ESPN doesn't have play-by-play data for all games.
    """
    soup = make_soup(ESPN_URL + 
        "/ncb/scoreboard?confId=50&date={0}".format(date))
    games = soup.find_all("span",
        {"id": lambda x: x and x.lower().endswith("-gamelinks-expand")})
    link_sets = [game.find_all("a") for game in games]
    
    play_by_plays = []
    for link_set in link_sets:
        for link in link_set:
            href = link.get("href")
            if "playbyplay" in href:
                play_by_plays.append(href)

    return play_by_plays


def get_play_by_play(pbp_path):
    "Returns the play-by-play data for a given game id."
    soup = make_soup(ESPN_URL + pbp_path)
    table = soup.find("table", "mod-data mod-pbp")
    rows = [row.find_all("td") for row in table.find_all("tr",
        lambda x: x in ("odd", "even"))]

    data = []
    for row in rows:
        values = []
        for value in row:
            if value.string is None:
                values.append(u"")
            else:
                values.append(value.string.replace(u"\xa0", u""))
        # handle timeouts being colspan=3
        # repeat the timeout or note in the other columns
        if len(values) != 4:
            values = [values[0], values[1], values[1], values[1]]
        data.append(values)

    return data


if __name__ == '__main__':
    try:
        START_DATE = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        END_DATE = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    except IndexError:
        print "I need a start and end date ('YYYY-MM-DD')."
        sys.exit()

    d = START_DATE
    delta = timedelta(days=1)
    while d <= END_DATE:
        print "Getting data for: {0}".format(d.strftime("%Y-%m-%d"))
        
        games = get_games(d.strftime("%Y%m%d"))
        for game in games:
            game_id = game.lower().split("gameid=")[1]

            # I didn't feel like dealing with unicode characters
            try:
                print "Writing data for game: {0}".format(game_id)
                with open("cbb-play-data/" + game_id + ".psv", "w") as f:
                    writer = csv.writer(f, delimiter="|")
                    writer.writerow(["time", "away", "score", "home"])
                    writer.writerows(get_play_by_play(game))
            except UnicodeEncodeError:
                print "Unable to write data for game: {0}".format(game_id)
                print "Moving on ..."
                continue

        d += delta
        sleep(2) # be nice