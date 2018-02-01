FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bs4"]
RUN ["pip", "install", "clint"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "splinter"]
RUN ["pip", "install", "youtube_dl"]
CMD ["python", "snippet.py"]