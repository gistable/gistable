import gspread
from newspaper import Article
from bs4 import BeautifulSoup
import requests
import re
import time
import feedparser

# Login with your Google account
gc = gspread.login('megmailaccount', 'mepassword')

# Open a worksheet from spreadsheet with one shot
wks = gc.open("Morning App feed").sheet1
data = wks.get_all_values()
scraped_urls = [i[3] for i in data[1:]]


def format(text):
    #remove content inside round brackets
    text =  re.sub(r'\[(?:[^\]|]*\|)?([^\]|]*)\]', '', text)
    #remove content inside round brackets
    text = re.sub(r'\([^)]*\)', '', text)
    text = text.strip()
    return text

def addToSpreadsheet(title,url):
    article= Article(url)
    article.download()
    article.parse()
    image = article.top_image
    wks.insert_row([time.strftime("%d/%m/%Y"),"some category",title,url,image],index=2)

def scrapeRedditArticles(limit=6,url="http://www.reddit.com/r/GetMotivated/search.json?q=flair%3Aarticle&sort=top&restrict_sr=on&t=week"):
    reddit_url = url
    headers = {'User-Agent' : 'this is a simple reddit bot by /u/tomarina'}
    reddit_json = requests.get(reddit_url,headers=headers).json()
    
    for i in reddit_json["data"]["children"][:6]:
        if i['data']['is_self'] == True: continue
        if i['data']['over_18'] == True: continue
        if i["data"]["url"] in scraped_urls: continue
        title = format(i["data"]["title"])
        url = i["data"]["url"]
        print title,url
        addToSpreadsheet(title,url)
        
def scrapeQuotes(limit=3):
    scrapeRedditArticles(limit,url="http://www.reddit.com/r/GetMotivated/search.json?q=flair%3Aimage&sort=top&restrict_sr=on&t=week")

def scrapeLifehacker(limit=4):
    url = "http://lifehacker.com/tag/motivation"
    data  = requests.get(url).text
    soup = BeautifulSoup(data)
    
    for item in soup.select("div.post-list > div.post-wrapper")[:limit]:
        title = item.select("h1.headline")[0].get_text()
        url = item.select("h1.headline > a")[0].get("href")
        if url in scraped_urls:continue
        print title,url
        addToSpreadsheet(title,url)

def scrapeHuffPost(limit=4):
    url = "http://www.huffingtonpost.com/feeds/verticals/good-news/index.xml"
    d = feedparser.parse(url)

    for item in d["entries"][:limit]:
        title = item['title']
        url = item['link']
        print title,url,pubdate
        addToSpreadsheet(title,url)


def scrapeEntrepreneur(limit=4):
    url = "http://www.entrepreneur.com/topic/motivation"
    data  = requests.get(url).text
    soup = BeautifulSoup(data)
    
    for item in soup.select("div.adrt-content > div.row > div.col-md-12 > div.pl")[:limit]:
        title = item.select("h3 > a")[0].get_text()
        url = item.select("h3 > a")[0].get('href')
        url = "http://www.entrepreneur.com"+url
        print title,url
        addToSpreadsheet(title,url)


def dailyCron():
    scrapeRedditArticles(2)
    scrapeEntrepreneur(2)
    scrapeQuotes(1)
    scrapeLifehacker(2)
    scrapeHuffPost(2)
    scrapeEntrepreneur(2)
    scrapeQuotes(1)

if __name__ == '__main__':
    dailyCron()
