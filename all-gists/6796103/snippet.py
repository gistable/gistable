import urllib
import json
from bs4 import BeautifulSoup
from collections import namedtuple

Video = namedtuple("Video", "video_id title duration views thumbnail")

def parse_video_div(div):
    video_id = div.get("data-context-item-id", "")
    title = div.find("a", "yt-uix-tile-link").text
    duration = div.find("span", "video-time").contents[0].text
    views = int(div.find("ul", "yt-lockup-meta-info").contents[0].text.rstrip(" views").replace(",", ""))
    img = div.find("img")
    thumbnail = "http:" + img.get("src", "") if img else ""
    return Video(video_id, title, duration, views, thumbnail)

def parse_videos_page(page):
    video_divs = page.find_all("div", "yt-lockup-video")
    return [parse_video_div(div) for div in video_divs]

def find_load_more_url(page):
    for button in page.find_all("button"):
        url = button.get("data-uix-load-more-href")
        if url:
            return "http://www.youtube.com" + url

def download_page(url):
    print("Downloading {0}".format(url))
    return urllib.urlopen(url).read()

def get_videos(username):
    page_url = "http://www.youtube.com/user/{0}/videos".format(username)
    page = BeautifulSoup(download_page(page_url))
    videos = parse_videos_page(page)
    page_url = find_load_more_url(page)
    while page_url:
        json_data = json.loads(download_page(page_url))
        page = BeautifulSoup(json_data.get("content_html", ""))
        videos.extend(parse_videos_page(page))
        page_url = find_load_more_url(BeautifulSoup(json_data.get("load_more_widget_html", "")))
    return videos

if __name__ == "__main__":
    videos = get_videos("jimmydiresta")
    for video in videos:
        print(video)
    print("{0} videos".format(len(videos)))
