from selenium import webdriver
import time
import os
import datetime as dt
from BeautifulSoup import BeautifulSoup
from pyvirtualdisplay import Display
import json
import sys,getopt
import datetime
chromedriver = "/usr/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
display = Display(visible=0, size=(800, 600))
display.start()
driver = webdriver.Chrome(chromedriver)
# driver = webdriver.Firefox()
url = "http://www.flashscore.com"
driver.implicitly_wait(10)
list_of_sports = ['soccer', 'tennis', 'baseball', 'american-football', 'hockey', 'basketball']

def get_json_of_sport(sport, sport_web_driver, date, data):

    table_main = sport_web_driver.find_element_by_class_name('table-main')
    soup = BeautifulSoup(table_main.get_attribute('innerHTML'))
    for table in soup.findAll("table", {"class": sport}):
        league = table.find("span", {"class": 'country_part'}).text
        nation = table.find("span", {"class": 'tournament_part'}).text

        print "-------------------------------------------------------------------------------------------"
        print table.find("span", {"class": 'country_part'}).text, table.find("span", {"class": 'tournament_part'}).text
        print "--------------------------------------------------------------------------------------------"

        trs = table.findAll("tr", {"class": lambda x: x and "stage-scheduled" in x.split()}) or \
              table.findAll("tr", {"class": lambda x: x and "stage-finished" in x.split()}) or \
              table.findAll("tr", {"class": lambda x: x and "stage-live" in x.split()})


        for index, tr in enumerate(trs):
            match_json = {}
            try:
                time_of_match = tr.find("td", {"class": lambda x: x and "time" in x.split()}).text
            except:
                continue
            team_home = tr.find("td", {"class": lambda x: x and "team-home" in x.split()}).text
            try:
                team_away = tr.find("td", {"class": lambda x: x and "team-away" in x.split()}).text

            except:
                team_away = trs[index+1].find("td", {"class": lambda x: x and "team-away" in x.split()}).text


            match_json['homeTeam'] = team_home
            match_json['awayTeam'] = team_away
            match_json['Date'] = date
            match_json['Hour'] = time_of_match
            match_json['League'] = league
            match_json['Nation'] = nation
            data.append(set(match_json))
            print time_of_match, team_home, team_away


for sport in list_of_sports:
    url2 = url + '/' + sport + '/'
    driver.get(url2)
    time.sleep(10)
    days = 7

    date_of_match = ''
    if  sys.argv[1:]:
        print "=================================="
        argv = sys.argv[1:]
        for i in argv:
            date_of_match = datetime.datetime.strptime(i,'%Y/%m/%d').strftime("%Y/%m/%d")
    else:
        print "dfdfdf"
        date_of_match = dt.datetime.now().strftime("%Y/%m/%d")

    date_int = dt.datetime.now()
    for i in range(0, days):
        data = []

        get_json_of_sport(sport, driver, date_of_match, data)
        json_data = json.dumps(data)

        date_string = date_int.strftime("%Y_%m_%d")
        print json_data
        filename = sport + "_" + date_string + '.txt'
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, 'w') as outfile:
            json.dump(json_data, outfile)
        time.sleep(10)
        print "\n"
        try:
            driver.find_element_by_css_selector('span.day.tomorrow').click()
        except:
            break

        date_int = dt.datetime.now() + dt.timedelta(days=1)
        # date_of_match = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%Y/%m/%d")

        date_of_match = ''
        if  sys.argv[1:]:
            print"----------------"
            argv = sys.argv[1:]
            for i in argv:
                date_of_match = datetime.datetime.strptime(i,'%Y/%m/%d').strftime("%Y/%m/%d")+ dt.timedelta(days=1).strftime("%Y/%m/%d")
        else:
            print "fdfdf"
            date_of_match = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%Y/%m/%d")

driver.close()









