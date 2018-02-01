FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "simplegeo"]
RUN ["pip", "install", "feedparser"]
RUN ["pip", "install", "tweepy"]
CMD ["python", "snippet.py"]