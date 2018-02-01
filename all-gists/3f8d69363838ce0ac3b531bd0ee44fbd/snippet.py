from googleapiclient.discovery import build
import datetime
import re
import sys
import youtube_dl
import os
from typing import List

#I have no idea why this line is needed but without it nothing works
sys.modules['win32file'] = None

#For API
DEVELOPER_KEY = ""
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube_build = build(YOUTUBE_API_SERVICE_NAME,
                                   YOUTUBE_API_VERSION,
                                   developerKey=DEVELOPER_KEY)
max_results = 25
max_duration = 20

#For youtubedl
YOUTUBE_DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
YOUTUBE_DEFAULT_OUTTMPL = '%(title)s.%(ext)s'
YOUTUBE_SIMULATE_DOWNLOAD = False
video_format = 'bestaudio/best'
key = 'FFmpegExtractAudio'
preferredcodec = 'mp3'
preferredquality = '192'
outtmpl = os.path.join(YOUTUBE_DOWNLOAD_DIR, YOUTUBE_DEFAULT_OUTTMPL)
ydl_options = {
            'format': video_format,
            'postprocessors': [{
                'key': key,
                'preferredcodec': preferredcodec,
                'preferredquality': preferredquality,
            }],
            'outtmpl': outtmpl,
            'simulate': YOUTUBE_SIMULATE_DOWNLOAD,
            'prefer_ffmpeg': True
        }


def get_video_ids(channel_id: str, date_after: 'datetime') -> List[str]:

    iso_time = date_to_zulu_format(date_after)
    search_response = youtube_build.search().list(
        channelId=channel_id,
        part="id, snippet",
        maxResults=max_results,
        publishedAfter=iso_time
    ).execute()
    youtube_video_ids = list()

    for search_result in search_response.get("items", []):
        kind = search_result["id"]["kind"]
        if kind == "youtube#video":


            video_id = search_result["id"]["videoId"]
            duration = get_video_duration(video_id)
            if duration > max_duration:
                continue
            youtube_video_ids.append(video_id)

    return youtube_video_ids


def get_video_duration(video_id: str) -> int:
    search_response = youtube_build.videos().list(
        part='contentDetails',
        id=video_id
    ).execute()
    duration = search_response["items"][0]['contentDetails']['duration']
    regex_pattern = r'PT((\d+)H)?((\d+)M)?((\d+)S)?'
    result = re.search(regex_pattern, duration)
    hours = 0
    minutes = 0
    if result:
        if result.group(2):
            hours = int(result.group(2))
        if result.group(4):
            minutes = int(result.group(4))
    ret_duration = minutes + hours * 60
    return ret_duration


def date_to_zulu_format(datetime_to_convert: 'datetime') -> 'datetime':
    normal_datetime = datetime.datetime.combine(datetime_to_convert, datetime.datetime.min.time())
    zulu_time = normal_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    return zulu_time


def download_videos(channel_ids: List[str], date_after: 'datetime') -> None:
    for channel_id in channel_ids:
        video_ids = get_video_ids(channel_id, date_after)
        download_videos_by_ids(video_ids)


def download_videos_by_ids(youtube_video_ids: List[str]) -> None:
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        ydl.download(youtube_video_ids)

channel_ids = ["UCrOaijB2OTbuH0Sc7Ifee1A"]
date_after = datetime.datetime.now() - datetime.timedelta(days=4)
download_videos(channel_ids, date_after)