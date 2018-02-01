"""
#Eksi entry crawler
#Python 3.5
#Mongodb - Beautifulsoup example

requirements.txt
----
pymongo
requests
beautifulsoup4
html5lib
joblib
----
"""
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from joblib import Parallel, delayed
import multiprocessing

client = MongoClient('localhost', 27017)
db = client['eksi-db']


def add_db(entry):
    try:
        result = db.entry.insert_one(entry)
    except Exception as e:
        print(str(e))
    return result


def get_status(text):
    """
    # -1 : hiç olmadı
    #  0 : silinmiş
    #  2 : var
    """
    if len(text) == 3581:
        return -1
    elif text.find('data-not-found="true"') != -1:
        return 0
    else:
        return 1


def make_url(text):
    return 'https://eksisozluk.com' + text


def get_title(text):
    title = {
        "id": text.find("div", {"id": "topic"}).find("h1")["data-id"],
        "title": text.find("div", {"id": "topic"}).find("h1")["data-title"],
        "url": make_url(text.find("div", {"id": "topic"}).find("a")["href"])
    }
    return title


def get_author(text):
    author = {
        "id": text.find("ul", {'id': 'entry-list'}).find("li")["data-author-id"],
        "name": text.find("ul", {'id': 'entry-list'}).find("li")["data-author"],
        "url": make_url(text.find("div", {"class": "info"}).find("a", {"class": "entry-author"})["href"])
    }
    return author


def get_date(text):
    return text.find("div", {"class": "info"}).find("a", {"class": "entry-date"}).text


def get_favorite_count(text):
    return text.find("ul", {'id': 'entry-list'}).find("li")["data-favorite-count"]


def get_content(text):
    return text.find("div", {'class': 'content'}).text.strip().replace("\n", "").replace("\r", "")


def get_entry(entry_id):
    url = make_url("/entry/" + str(entry_id))
    r = requests.get(url)
    status = get_status(r.text)
    if status == 1:
        beauty_text = BeautifulSoup(r.text, "html5lib")
        entry = {"id": entry_id,
                 "status": status,
                 "url": url,
                 "content": get_content(beauty_text),
                 "date": get_date(beauty_text),
                 "favorite_count": get_favorite_count(beauty_text),
                 "title": get_title(beauty_text),
                 "author": get_author(beauty_text),
                 }
    else:
        entry = {"id": entry_id,
                 "status": status}
    add_db(entry)
    pass


# entry start-end id
start = 1
end = 100000
num_cores = multiprocessing.cpu_count()
print(num_cores)
Parallel(n_jobs=num_cores)(delayed(get_entry)(i) for i in range(start, end))
print("end")
