FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "selenium"]
RUN ["pip", "install", "mechanize"]
CMD ["python", "snippet.py"]