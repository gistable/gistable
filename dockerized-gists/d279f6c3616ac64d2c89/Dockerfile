FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pypyodbc"]
RUN ["pip", "install", "tweepy"]
RUN ["pip", "install", "colorama"]
RUN ["pip", "install", "tweepy"]
CMD ["python", "snippet.py"]