import requests
import time
import csv
from bs4 import BeautifulSoup

def main(sourcefile):
    url_template = "https://tools.wmflabs.org/sourcemd/?id={0}&doit=Check+source"

    with open(sourcefile) as f:
        csvdump = csv.reader(f)
        for row in csvdump:

            r = requests.get(url_template.format(row[0]))

            if r.status_code != 200:
                if r.status_code == 503:
                    time.sleep(300) # wait for five minutes and try again
                    r = requests.get(url_template.format(row[0]))
                    if r.status_code != 200:
                        raise Exception(url_template.format(row[0]) + " returns an error of: " + str(r.status_code))
                else:
                    raise Exception(url_template.format(row[0]) + " returns an error of: " + str(r.status_code))

            soup = BeautifulSoup(r.text, "html.parser")
            
            textarea = soup.find_all("textarea")

            if len(textarea) == 1:
                textarea = textarea[0].contents[0]
                print(textarea)

main("doi.csv")