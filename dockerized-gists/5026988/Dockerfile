FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bs4"]
RUN ["pip", "install", "mechanize"]
RUN ["pip", "install", "bitly_api"]
CMD ["python", "snippet.py"]